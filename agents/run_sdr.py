"""
ForceIA - Runtime dos agentes (SDR / Closer / Follow-up)
com persistencia no Supabase, sync Twenty e envio via Evolution API.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from dotenv import load_dotenv
from openai import OpenAI

from db import add_message, get_history, get_lead_by_phone, log_event, merge_metadata, set_stage, upsert_lead
from prompts import load_prompt
from state_machine import detect_stage_from_reply, next_agent_for_stage

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "forceia-dev-key")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "forceia")

client = OpenAI(api_key=OPENAI_API_KEY)


def send_whatsapp(number: str, text: str) -> dict:
    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"}
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


def generate_reply(agent: str, history: list[dict], user_message: str) -> str:
    messages = build_messages(agent, history, user_message)
    response = client.chat.completions.create(
        model=os.getenv("GPT_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content or ""


def sync_twenty(lead: dict) -> None:
    try:
        from twenty_client import enabled, sync_lead_to_twenty

        if not enabled():
            return
        result = sync_lead_to_twenty(lead)
        if result.get("person_id"):
            merge_metadata(
                lead["phone"],
                {
                    "twenty_person_id": result.get("person_id"),
                    "twenty_opportunity_id": result.get("opportunity_id"),
                },
            )
            log_event(lead.get("id"), "twenty_synced", result)
    except Exception as exc:
        log_event(lead.get("id"), "twenty_sync_error", {"error": str(exc)})


def handle_incoming(number: str, text: str, send: bool = True) -> str:
    """Processa mensagem: carrega lead, escolhe agente, responde, persiste e sincroniza Twenty."""
    lead = get_lead_by_phone(number)
    if not lead:
        lead = upsert_lead(number, stage="sdr")
        log_event(lead["id"], "lead_created", {"phone": number})
        sync_twenty(lead)

    stage = lead.get("stage") or "sdr"
    agent = next_agent_for_stage(stage)
    history_rows = get_history(lead["id"], limit=20)
    history = [{"role": r["role"], "content": r["content"]} for r in history_rows]

    reply = generate_reply(agent, history, text)
    new_stage = detect_stage_from_reply(reply, stage)

    add_message(lead["id"], "user", text)
    add_message(lead["id"], "assistant", reply, agent=agent)

    if new_stage != stage:
        lead = set_stage(number, new_stage)
        log_event(lead["id"], "stage_changed", {"from": stage, "to": new_stage})
        sync_twenty(lead)
    else:
        upsert_lead(number)
        # sync periodico leve: so se ainda nao tiver person no metadata
        meta = lead.get("metadata") or {}
        if not meta.get("twenty_person_id"):
            lead = get_lead_by_phone(number) or lead
            sync_twenty(lead)

    if send:
        try:
            send_whatsapp(number, reply)
        except Exception as exc:
            log_event(lead["id"], "whatsapp_send_error", {"error": str(exc)})

    return reply


if __name__ == "__main__":
    print("ForceIA Agent - modo teste local (sem WhatsApp)")
    print("Digite mensagens (ou 'sair'). Usa Supabase + Twenty se configurados.\n")
    phone = "5511999999999"
    while True:
        user = input("Lead: ").strip()
        if user.lower() in ("sair", "exit", "quit"):
            break
        try:
            reply = handle_incoming(phone, user, send=False)
            print(f"Agente: {reply}\n")
        except Exception as e:
            print(f"Erro: {e}\n")
            from prompts import load_prompt

            msgs = [
                {"role": "system", "content": load_prompt("sdr")},
                {"role": "user", "content": user},
            ]
            r = client.chat.completions.create(
                model=os.getenv("GPT_MODEL", "gpt-4o-mini"),
                messages=msgs,
            )
            print(f"SDR (local): {r.choices[0].message.content}\n")
