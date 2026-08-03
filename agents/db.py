"""ForceIA - Cliente Supabase para leads e mensagens."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("Defina SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no .env")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def upsert_lead(phone: str, **fields: Any) -> dict:
    client = get_client()
    payload = {"phone": phone, **{k: v for k, v in fields.items() if v is not None}}
    payload["last_message_at"] = datetime.now(timezone.utc).isoformat()
    result = (
        client.table("leads")
        .upsert(payload, on_conflict="phone")
        .execute()
    )
    return result.data[0] if result.data else payload


def get_lead_by_phone(phone: str) -> dict | None:
    client = get_client()
    result = client.table("leads").select("*").eq("phone", phone).limit(1).execute()
    return result.data[0] if result.data else None


def set_stage(phone: str, stage: str) -> dict:
    return upsert_lead(phone, stage=stage)


def add_message(lead_id: str, role: str, content: str, agent: str | None = None) -> dict:
    client = get_client()
    row = {
        "lead_id": lead_id,
        "role": role,
        "content": content,
        "agent": agent,
    }
    result = client.table("messages").insert(row).execute()
    return result.data[0] if result.data else row


def get_history(lead_id: str, limit: int = 20) -> list[dict]:
    client = get_client()
    result = (
        client.table("messages")
        .select("role, content, agent, created_at")
        .eq("lead_id", lead_id)
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data or []


def log_event(lead_id: str | None, event_type: str, payload: dict | None = None) -> None:
    client = get_client()
    client.table("events").insert(
        {
            "lead_id": lead_id,
            "type": event_type,
            "payload": payload or {},
        }
    ).execute()
