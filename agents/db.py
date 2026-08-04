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


def get_lead_by_id(workspace_id: str, lead_id: str) -> dict | None:
    """Lead por id, garantindo pertencer ao workspace (multi-tenant)."""
    result = (
        get_client()
        .table("leads")
        .select("*")
        .eq("workspace_id", workspace_id)
        .eq("id", lead_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


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


def was_message_processed(workspace_id: str, message_id: str) -> bool:
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
        .select("id, phone, name, company, email, stage, bant, last_message_at, updated_at, metadata")
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


def list_leads_by_stage(workspace_id: str, stage: str, limit: int = 20) -> list[dict]:
    result = (
        get_client()
        .table("leads")
        .select("id, phone, name, company, stage, bant, metadata, updated_at")
        .eq("workspace_id", workspace_id)
        .eq("stage", stage)
        .order("updated_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


def get_messages_for_lead(lead_id: str, limit: int = 100) -> list[dict]:
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


def create_learning_run(workspace_id: str | None = None) -> dict:
    row = {"status": "running", "workspace_id": workspace_id}
    result = get_client().table("learning_runs").insert(row).execute()
    return result.data[0] if result.data else row


def finish_learning_run(
    run_id: str,
    *,
    status: str,
    won_sampled: int = 0,
    lost_sampled: int = 0,
    summary: str | None = None,
    error: str | None = None,
) -> None:
    from datetime import UTC, datetime

    get_client().table("learning_runs").update(
        {
            "status": status,
            "won_sampled": won_sampled,
            "lost_sampled": lost_sampled,
            "summary": summary,
            "error": error,
            "finished_at": datetime.now(UTC).isoformat(),
        }
    ).eq("id", run_id).execute()


def insert_prompt_suggestion(**fields) -> dict:
    result = get_client().table("prompt_suggestions").insert(fields).execute()
    return result.data[0] if result.data else fields


def list_prompt_suggestions(
    *,
    status: str | None = "pending",
    workspace_id: str | None = None,
    limit: int = 50,
) -> list[dict]:
    q = get_client().table("prompt_suggestions").select("*")
    if status:
        q = q.eq("status", status)
    if workspace_id:
        q = q.eq("workspace_id", workspace_id)
    result = q.order("created_at", desc=True).limit(limit).execute()
    return result.data or []


def get_prompt_suggestion(suggestion_id: str) -> dict | None:
    result = (
        get_client()
        .table("prompt_suggestions")
        .select("*")
        .eq("id", suggestion_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def update_prompt_suggestion(suggestion_id: str, **fields) -> dict:
    result = (
        get_client()
        .table("prompt_suggestions")
        .update(fields)
        .eq("id", suggestion_id)
        .execute()
    )
    return result.data[0] if result.data else fields


def upsert_prompt_override(
    agent: str,
    content: str,
    *,
    workspace_id: str | None = None,
    source_suggestion_id: str | None = None,
) -> dict:
    client = get_client()
    payload = {
        "agent": agent,
        "content": content,
        "workspace_id": workspace_id,
        "source_suggestion_id": source_suggestion_id,
        "active": True,
    }
    if workspace_id:
        result = (
            client.table("agent_prompt_overrides")
            .upsert(payload, on_conflict="workspace_id,agent")
            .execute()
        )
    else:
        existing = (
            client.table("agent_prompt_overrides")
            .select("id")
            .is_("workspace_id", "null")
            .eq("agent", agent)
            .limit(1)
            .execute()
        )
        if existing.data:
            result = (
                client.table("agent_prompt_overrides")
                .update(payload)
                .eq("id", existing.data[0]["id"])
                .execute()
            )
        else:
            result = client.table("agent_prompt_overrides").insert(payload).execute()
    return result.data[0] if result.data else payload


def get_prompt_override(agent: str, workspace_id: str | None = None) -> str | None:
    client = get_client()
    if workspace_id:
        result = (
            client.table("agent_prompt_overrides")
            .select("content")
            .eq("workspace_id", workspace_id)
            .eq("agent", agent)
            .eq("active", True)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0].get("content")
    result = (
        client.table("agent_prompt_overrides")
        .select("content")
        .is_("workspace_id", "null")
        .eq("agent", agent)
        .eq("active", True)
        .limit(1)
        .execute()
    )
    return result.data[0]["content"] if result.data else None
