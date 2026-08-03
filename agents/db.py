"""ForceIA - Cliente Supabase multi-tenant."""

from __future__ import annotations

import os
from datetime import UTC, datetime
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


# ---------- Workspaces ----------

def get_workspace_by_id(workspace_id: str) -> dict | None:
    result = get_client().table("workspaces").select("*").eq("id", workspace_id).limit(1).execute()
    return result.data[0] if result.data else None


def get_workspace_by_slug(slug: str) -> dict | None:
    result = get_client().table("workspaces").select("*").eq("slug", slug).eq("active", True).limit(1).execute()
    return result.data[0] if result.data else None


def get_workspace_by_api_key(api_key: str) -> dict | None:
    result = (
        get_client()
        .table("workspaces")
        .select("*")
        .eq("api_key", api_key)
        .eq("active", True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def get_workspace_by_evolution_instance(instance: str) -> dict | None:
    result = (
        get_client()
        .table("workspaces")
        .select("*")
        .eq("evolution_instance", instance)
        .eq("active", True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def list_active_workspaces() -> list[dict]:
    result = get_client().table("workspaces").select("*").eq("active", True).execute()
    return result.data or []


def create_workspace(name: str, slug: str, **fields: Any) -> dict:
    payload = {"name": name, "slug": slug, **{k: v for k, v in fields.items() if v is not None}}
    result = get_client().table("workspaces").insert(payload).execute()
    return result.data[0] if result.data else payload


# ---------- Leads ----------

def upsert_lead(workspace_id: str, phone: str, **fields: Any) -> dict:
    client = get_client()
    payload = {
        "workspace_id": workspace_id,
        "phone": phone,
        **{k: v for k, v in fields.items() if v is not None},
    }
    payload["last_message_at"] = datetime.now(UTC).isoformat()
    result = client.table("leads").upsert(payload, on_conflict="workspace_id,phone").execute()
    return result.data[0] if result.data else payload


def get_lead_by_phone(workspace_id: str, phone: str) -> dict | None:
    result = (
        get_client()
        .table("leads")
        .select("*")
        .eq("workspace_id", workspace_id)
        .eq("phone", phone)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def set_stage(workspace_id: str, phone: str, stage: str) -> dict:
    return upsert_lead(workspace_id, phone, stage=stage)


def add_message(lead_id: str, role: str, content: str, agent: str | None = None) -> dict:
    row = {"lead_id": lead_id, "role": role, "content": content, "agent": agent}
    result = get_client().table("messages").insert(row).execute()
    return result.data[0] if result.data else row


def get_history(lead_id: str, limit: int = 20) -> list[dict]:
    result = (
        get_client()
        .table("messages")
        .select("role, content, agent, created_at")
        .eq("lead_id", lead_id)
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data or []


def log_event(
    event_type: str,
    payload: dict | None = None,
    lead_id: str | None = None,
    workspace_id: str | None = None,
) -> None:
    get_client().table("events").insert(
        {
            "type": event_type,
            "payload": payload or {},
            "lead_id": lead_id,
            "workspace_id": workspace_id,
        }
    ).execute()


def merge_metadata(workspace_id: str, phone: str, extra: dict) -> dict:
    lead = get_lead_by_phone(workspace_id, phone) or {}
    meta = dict(lead.get("metadata") or {})
    meta.update(extra)
    return upsert_lead(workspace_id, phone, metadata=meta)


# ---------- Idempotencia de mensagens ----------

def was_message_processed(workspace_id: str, message_id: str) -> bool:
    """Verifica se um message_id da Evolution ja foi processado (dedup de webhook)."""
    if not message_id:
        return False
    result = (
        get_client()
        .table("events")
        .select("id")
        .eq("type", "message_processed")
        .eq("workspace_id", workspace_id)
        .contains("payload", {"message_id": message_id})
        .limit(1)
        .execute()
    )
    return bool(result.data)


def mark_message_processed(
    workspace_id: str, message_id: str, lead_id: str | None = None
) -> None:
    if not message_id:
        return
    log_event(
        "message_processed",
        {"message_id": message_id},
        lead_id=lead_id,
        workspace_id=workspace_id,
    )


# ---------- Consultas para o painel admin ----------

def count_leads_by_stage(workspace_id: str) -> dict[str, int]:
    result = (
        get_client()
        .table("leads")
        .select("stage")
        .eq("workspace_id", workspace_id)
        .execute()
    )
    counts: dict[str, int] = {}
    for row in result.data or []:
        stage = row.get("stage") or "sdr"
        counts[stage] = counts.get(stage, 0) + 1
    return counts


def list_leads(workspace_id: str, limit: int = 100) -> list[dict]:
    result = (
        get_client()
        .table("leads")
        .select("id, phone, name, company, stage, last_message_at, updated_at, metadata")
        .eq("workspace_id", workspace_id)
        .order("updated_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


def list_recent_events(workspace_id: str, limit: int = 50) -> list[dict]:
    result = (
        get_client()
        .table("events")
        .select("type, payload, lead_id, created_at")
        .eq("workspace_id", workspace_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []
