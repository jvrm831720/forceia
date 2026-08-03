"""
ForceIA - Runtime multi-tenant dos agentes.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv
from openai import OpenAI

from db import (
    add_message,
    get_history,
    get_lead_by_phone,
    log_event,
    merge_metadata,
    set_stage,
    upsert_lead,
)
from prompts import load_prompt
from state_machine import detect_stage_from_reply, next_agent_for_stage
from workspace_context import WorkspaceContext, resolve_workspace

load_dotenv()


def send_whatsapp(ws: WorkspaceContext, number: str, text: str) -> dict:
    url = f"{ws.evolution_api_url.rstrip('/')}/message/sendText/{ws.evolution_instance}"
    headers = {"apikey": ws.evolution_api_key, "Content-Type": "application/json"}
    payload = {"number": number, "text": text}
    with httpx.Client(timeout=30) as http:
        r = http.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()


def build_messages(agent: str, history: list[dict], user_message: str) -> list[dict]:
    system = load_prompt(agent)
    messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
    for h in history:
        role = h.get("role")
        content = h.get("content")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})
    return messages


def generate_reply(ws: WorkspaceContext, agent: str, history: list[dict], user_message: str) -> str:
    client = OpenAI(api_key=ws.openai_api_key)
    messages = build_messages(agent, history, user_message)
    response = client.chat.completions.create(
        model=ws.gpt_model,
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content or ""


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


def handle_incoming(
    number: str,
    text: str,
    *,
    workspace: WorkspaceContext,
    send: bool = True,
) -> str:
    ws = workspace
    lead = get_lead_by_phone(ws.id, number)
    if not lead:
        lead = upsert_lead(ws.id, number, stage="sdr")
        log_event("lead_created", {"phone": number}, lead_id=lead["id"], workspace_id=ws.id)
        sync_twenty(ws, lead)

    stage = lead.get("stage") or "sdr"
    agent = next_agent_for_stage(stage)
    history_rows = get_history(lead["id"], limit=20)
    history = [{"role": r["role"], "content": r["content"]} for r in history_rows]

    reply = generate_reply(ws, agent, history, text)
    new_stage = detect_stage_from_reply(reply, stage)

    add_message(lead["id"], "user", text)
    add_message(lead["id"], "assistant", reply, agent=agent)

    if new_stage != stage:
        lead = set_stage(ws.id, number, new_stage)
        log_event(
            "stage_changed",
            {"from": stage, "to": new_stage},
            lead_id=lead["id"],
            workspace_id=ws.id,
        )
        sync_twenty(ws, lead)
    else:
        upsert_lead(ws.id, number)
        meta = lead.get("metadata") or {}
        if not meta.get("twenty_person_id"):
            lead = get_lead_by_phone(ws.id, number) or lead
            sync_twenty(ws, lead)

    if send:
        try:
            send_whatsapp(ws, number, reply)
        except Exception as exc:
            log_event(
                "whatsapp_send_error",
                {"error": str(exc)},
                lead_id=lead["id"],
                workspace_id=ws.id,
            )

    return reply


if __name__ == "__main__":
    print("ForceIA Agent multi-tenant - teste local")
    slug = os.getenv("DEFAULT_WORKSPACE_SLUG", "default")
    ws = resolve_workspace(slug=slug)
    if not ws:
        print(f"Workspace '{slug}' nao encontrado. Crie no Supabase (tabela workspaces).")
        raise SystemExit(1)
    print(f"Workspace: {ws.name} ({ws.slug})\n")
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
