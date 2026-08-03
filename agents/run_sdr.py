"""
ForceIA - Runtime multi-tenant dos agentes (inteligencia + BANT + META).
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from db import (
    add_message,
    get_history,
    get_lead_by_phone,
    log_event,
    mark_message_processed,
    merge_metadata,
    set_stage,
    upsert_lead,
)
from dotenv import load_dotenv
from intelligence import (
    apply_meta_to_lead_fields,
    bant_score,
    build_system_prompt,
    is_bant_qualified,
    split_reply_and_meta,
    stage_from_meta_or_tags,
)
from logging_config import get_logger
from openai import OpenAI
from prompts import load_prompt
from state_machine import can_transition, next_agent_for_stage
from utils import strip_control_blocks
from workspace_context import WorkspaceContext, resolve_workspace

load_dotenv()

log = get_logger("forceia.agent")

_openai_clients: dict[str, OpenAI] = {}

_AGENT_TEMPERATURE = {
    "sdr": 0.65,
    "closer": 0.45,
    "followup": 0.7,
}


def _openai_client(api_key: str) -> OpenAI:
    client = _openai_clients.get(api_key)
    if client is None:
        client = OpenAI(api_key=api_key)
        _openai_clients[api_key] = client
    return client


def send_whatsapp(ws: WorkspaceContext, number: str, text: str) -> dict:
    url = f"{ws.evolution_api_url.rstrip('/')}/message/sendText/{ws.evolution_instance}"
    headers = {"apikey": ws.evolution_api_key, "Content-Type": "application/json"}
    payload = {"number": number, "text": text}
    with httpx.Client(timeout=30) as http:
        r = http.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()


def build_messages(
    agent: str,
    history: list[dict],
    user_message: str,
    *,
    lead: dict,
    workspace_name: str,
    workspace_id: str | None = None,
) -> list[dict]:
    base = load_prompt(agent, workspace_id=workspace_id)
    system = build_system_prompt(base, lead, workspace_name=workspace_name)
    messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
    for h in history:
        role = h.get("role")
        content = h.get("content")
        if role in ("user", "assistant") and content:
            if role == "assistant":
                content = strip_control_blocks(content)
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})
    return messages


def generate_reply(
    ws: WorkspaceContext,
    agent: str,
    history: list[dict],
    user_message: str,
    *,
    lead: dict | None = None,
    trace: Any = None,
) -> str:
    """Gera resposta bruta do modelo (pode conter ---META---)."""
    if not ws.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY nao configurada (workspace nem .env)")
    client = _openai_client(ws.openai_api_key)
    lead = lead or {"stage": "sdr", "bant": {}, "metadata": {}}
    messages = build_messages(
        agent,
        history,
        user_message,
        lead=lead,
        workspace_name=ws.name or "ForceIA",
        workspace_id=ws.id,
    )
    model = ws.gpt_model
    temperature = _AGENT_TEMPERATURE.get(agent, 0.6)
    lf_input = [
        {"role": m["role"], "content": (m.get("content") or "")[:1500]}
        for m in messages
        if m.get("role") != "system"
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=700,
    )
    content = response.choices[0].message.content or ""
    usage = None
    try:
        u = getattr(response, "usage", None)
        if u:
            usage = {
                "input": getattr(u, "prompt_tokens", None),
                "output": getattr(u, "completion_tokens", None),
                "total": getattr(u, "total_tokens", None),
            }
    except Exception:
        usage = None
    if trace is not None:
        try:
            trace.generation(
                name=f"openai.{agent}",
                model=model,
                input=lf_input,
                output=content[:4000],
                metadata={
                    "agent": agent,
                    "stage": (lead or {}).get("stage"),
                    "temperature": temperature,
                    "workspace": ws.slug,
                },
                usage=usage,
            )
        except Exception:
            pass
    return content


def sync_twenty(ws: WorkspaceContext, lead: dict) -> None:
    try:
        from twenty_client import sync_lead_to_twenty

        if not ws.twenty_api_url or not ws.twenty_api_key:
            return
        result = sync_lead_to_twenty(lead, api_url=ws.twenty_api_url, api_key=ws.twenty_api_key)
        if result.get("person_id"):
            merge_metadata(
                ws.id,
                lead["phone"],
                {
                    "twenty_person_id": result.get("person_id"),
                    "twenty_opportunity_id": result.get("opportunity_id"),
                },
            )
            log_event("twenty_synced", result, lead_id=lead.get("id"), workspace_id=ws.id)
    except Exception as exc:
        log_event(
            "twenty_sync_error",
            {"error": str(exc)},
            lead_id=lead.get("id"),
            workspace_id=ws.id,
        )


def _maybe_auto_qualify(stage: str, bant: dict | None, meta_stage: str) -> str:
    if stage == "sdr" and is_bant_qualified(bant) and meta_stage == stage:
        return "qualified"
    return meta_stage


def handle_incoming(
    number: str,
    text: str,
    *,
    workspace: WorkspaceContext,
    send: bool = True,
    message_id: str | None = None,
) -> str:
    """Entrada principal. Preferencia: LangGraph. Fallback: fluxo linear legado."""
    try:
        from graph import graph_enabled, invoke_turn

        if graph_enabled():
            reply = invoke_turn(
                workspace_id=workspace.id,
                phone=number,
                text=text,
                workspace_slug=workspace.slug,
                send=send,
                message_id=message_id,
            )
            log.info(
                "mensagem processada (langgraph)",
                extra={"workspace": workspace.slug, "phone": number},
            )
            return reply
    except Exception as exc:
        log.warning(
            "langgraph falhou, usando fluxo legado: %s",
            str(exc),
            extra={"workspace": workspace.slug, "phone": number},
        )

    return _handle_incoming_legacy(
        number, text, workspace=workspace, send=send, message_id=message_id
    )


def _handle_incoming_legacy(
    number: str,
    text: str,
    *,
    workspace: WorkspaceContext,
    send: bool = True,
    message_id: str | None = None,
) -> str:
    ws = workspace
    lead = get_lead_by_phone(ws.id, number)
    if not lead:
        lead = upsert_lead(ws.id, number, stage="sdr", bant={})
        log_event("lead_created", {"phone": number}, lead_id=lead["id"], workspace_id=ws.id)
        log.info("lead criado", extra={"workspace": ws.slug, "phone": number})
        sync_twenty(ws, lead)

    stage = lead.get("stage") or "sdr"
    if stage in ("won", "lost"):
        agent = "closer" if stage == "won" else "sdr"
    else:
        agent = next_agent_for_stage(stage)

    history_rows = get_history(lead["id"], limit=24)
    history = [{"role": r["role"], "content": r["content"]} for r in history_rows]

    raw_reply = generate_reply(ws, agent, history, text, lead=lead)
    visible, meta = split_reply_and_meta(raw_reply)
    reply = strip_control_blocks(visible)

    field_updates = apply_meta_to_lead_fields(lead, meta, text)
    new_stage = stage_from_meta_or_tags(raw_reply, meta, stage, can_transition)
    new_stage = _maybe_auto_qualify(stage, field_updates.get("bant") or lead.get("bant"), new_stage)

    if meta.get("handoff"):
        log_event(
            "handoff_requested",
            {"phone": number, "reason": meta.get("intent") or meta.get("notes")},
            lead_id=lead["id"],
            workspace_id=ws.id,
        )
        if "vou te conectar" not in reply.lower() and "humano" not in reply.lower():
            reply = (
                (reply + "\n\n" if reply else "")
                + "Vou acionar alguém do time para te atender em seguida, combinado?"
            ).strip()

    add_message(lead["id"], "user", text)
    add_message(lead["id"], "assistant", reply, agent=agent)
    if message_id:
        mark_message_processed(ws.id, message_id, lead_id=lead["id"])

    upsert_kwargs = {k: v for k, v in field_updates.items() if k != "metadata"}
    if field_updates.get("metadata"):
        merge_metadata(ws.id, number, field_updates["metadata"])
    if new_stage != stage:
        upsert_kwargs["stage"] = new_stage
        lead = set_stage(ws.id, number, new_stage)
        if upsert_kwargs:
            other = {k: v for k, v in upsert_kwargs.items() if k != "stage"}
            if other:
                lead = upsert_lead(ws.id, number, **other)
        log_event(
            "stage_changed",
            {
                "from": stage,
                "to": new_stage,
                "bant_score": bant_score(field_updates.get("bant") or lead.get("bant")),
            },
            lead_id=lead["id"],
            workspace_id=ws.id,
        )
        sync_twenty(ws, lead)
    else:
        if upsert_kwargs:
            lead = upsert_lead(ws.id, number, **upsert_kwargs)
        else:
            upsert_lead(ws.id, number)
        meta_lead = lead.get("metadata") or {}
        if not meta_lead.get("twenty_person_id"):
            lead = get_lead_by_phone(ws.id, number) or lead
            sync_twenty(ws, lead)

    log.info(
        "mensagem processada",
        extra={
            "workspace": ws.slug,
            "phone": number,
            "event": f"{stage}->{new_stage}",
            "stage": new_stage,
        },
    )

    if send and reply:
        try:
            send_whatsapp(ws, number, reply)
        except Exception as exc:
            log.warning(
                "falha ao enviar WhatsApp: %s",
                exc,
                extra={"workspace": ws.slug, "phone": number},
            )
            log_event(
                "whatsapp_send_error",
                {"error": str(exc)},
                lead_id=lead["id"],
                workspace_id=ws.id,
            )

    return reply


if __name__ == "__main__":
    print("ForceIA Agent multi-tenant - teste local (agentes inteligentes)")
    slug = os.getenv("DEFAULT_WORKSPACE_SLUG", "default")
    ws = resolve_workspace(slug=slug)
    if not ws:
        print(f"Workspace '{slug}' nao encontrado. Crie no Supabase (tabela workspaces).")
        raise SystemExit(1)
    print(f"Workspace: {ws.name} ({ws.slug})")
    print("Digite mensagens como o lead. 'sair' encerra.\n")
    phone = "5511999999999"
    while True:
        user = input("Lead: ").strip()
        if user.lower() in ("sair", "exit", "quit"):
            break
        try:
            reply = handle_incoming(phone, user, workspace=ws, send=False)
            print(f"Agente: {reply}\n")
        except Exception as e:
            print(f"Erro: {e}\n")
