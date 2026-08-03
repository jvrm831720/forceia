"""ForceIA - Cliente Supabase multi-tenant."""

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
    payload["last_message_at"] = datetime.now(timezone.utc).isoformat()
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
