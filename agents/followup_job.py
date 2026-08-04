"""ForceIA - Job de follow-up multi-tenant."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from typing import Any

from db import (
    add_message,
    get_history,
    list_active_workspaces,
    log_event,
    set_stage,
    upsert_lead,
)
from dotenv import load_dotenv
from intelligence import split_reply_and_meta
from logging_config import get_logger
from run_sdr import generate_reply
from utils import strip_control_blocks
from workspace_context import WorkspaceContext

load_dotenv()
log = get_logger("forceia.followup")


def candidates_for_workspace(ws: WorkspaceContext, stale_days: int | None = None) -> list[dict]:
    from db import get_client

    days = stale_days if stale_days is not None else ws.followup_stale_days
    cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
    result = (
        get_client()
        .table("leads")
        .select(
            "id, phone, name, company, stage, last_message_at, metadata, workspace_id, bant"
        )
        .eq("workspace_id", ws.id)
        .in_("stage", ["sdr", "qualified", "closer", "followup"])
        .lt("last_message_at", cutoff)
        .order("last_message_at", desc=False)
        .limit(40)
        .execute()
    )
    return result.data or []


def recent_followup_event(lead_id: str, hours: int) -> bool:
    from db import get_client

    since = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()
    result = (
        get_client()
        .table("events")
        .select("id")
        .eq("lead_id", lead_id)
        .eq("type", "followup_sent")
        .gte("created_at", since)
        .limit(1)
        .execute()
    )
    return bool(result.data)


def build_followup_context(lead: dict, history: list[dict]) -> str:
    name = lead.get("name") or ""
    company = lead.get("company") or ""
    stage = lead.get("stage") or "sdr"
    bant = lead.get("bant") or {}
    parts = [
        f"Lead stage={stage}.",
        f"Nome: {name or 'desconhecido'}.",
        f"Empresa: {company or 'desconhecida'}.",
    ]
    if bant:
        bits = [f"{k}={v}" for k, v in bant.items() if v]
        if bits:
            parts.append("BANT: " + "; ".join(bits))
    last_user = next((h["content"] for h in reversed(history) if h.get("role") == "user"), "")
    if last_user:
        parts.append(f"Ultima msg do lead: {last_user[:180]}")
    parts.append("Reative com valor, sem cobranca. Uma mensagem curta.")
    return " ".join(parts)


def process_lead(ws: WorkspaceContext, lead: dict, dry_run: bool = False) -> dict:
    lead_id = lead["id"]
    phone = lead["phone"]
    stage = lead.get("stage") or "sdr"

    try:
        from db import is_agent_paused
    except ImportError:
        is_agent_paused = lambda _l: False  # type: ignore

    if is_agent_paused(lead):
        return {
            "phone": phone,
            "workspace": ws.slug,
            "status": "skipped",
            "reason": "agent_paused",
        }

    if recent_followup_event(lead_id, ws.followup_min_hours):
        return {
            "phone": phone,
            "workspace": ws.slug,
            "status": "skipped",
            "reason": "followup_recente",
        }

    history_rows = get_history(lead_id, limit=16)
    history = [{"role": r["role"], "content": r["content"]} for r in history_rows]
    raw = generate_reply(
        ws,
        "followup",
        history,
        build_followup_context(lead, history),
        lead=lead,
    )
    visible, _meta = split_reply_and_meta(raw)
    reply = strip_control_blocks(visible)

    if dry_run:
        return {"phone": phone, "workspace": ws.slug, "status": "dry_run", "reply": reply}

    if stage != "followup":
        set_stage(ws.id, phone, "followup")
        log_event(
            "stage_changed",
            {"from": stage, "to": "followup", "source": "followup_job"},
            lead_id=lead_id,
            workspace_id=ws.id,
        )

    add_message(lead_id, "assistant", reply, agent="followup")
    upsert_lead(ws.id, phone)

    try:
        from run_sdr import send_whatsapp

        send_whatsapp(ws, phone, reply)
        log_event(
            "followup_sent",
            {"phone": phone},
            lead_id=lead_id,
            workspace_id=ws.id,
        )
        return {"phone": phone, "workspace": ws.slug, "status": "sent", "reply": reply}
    except Exception as exc:
        log_event(
            "followup_send_error",
            {"error": str(exc)},
            lead_id=lead_id,
            workspace_id=ws.id,
        )
        return {"phone": phone, "workspace": ws.slug, "status": "error", "error": str(exc)}


def run_followup_job(*, dry_run: bool = False, workspace_slug: str | None = None) -> list[dict]:
    results: list[dict] = []
    rows = list_active_workspaces()
    for row in rows:
        if workspace_slug and row.get("slug") != workspace_slug:
            continue
        ws = WorkspaceContext.from_row(row)
        for lead in candidates_for_workspace(ws):
            try:
                results.append(process_lead(ws, lead, dry_run=dry_run))
            except Exception as exc:
                results.append(
                    {
                        "phone": lead.get("phone"),
                        "workspace": ws.slug,
                        "status": "error",
                        "error": str(exc),
                    }
                )
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--workspace", default=None)
    args = parser.parse_args()
    out = run_followup_job(dry_run=args.dry_run, workspace_slug=args.workspace)
    for r in out:
        print(r)
