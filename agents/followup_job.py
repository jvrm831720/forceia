"""
ForceIA - Job de Follow-up multi-tenant (contexto BANT inteligente)

  python followup_job.py
  python followup_job.py --workspace demo
  python followup_job.py --all --dry-run
"""

from __future__ import annotations

import argparse
import os
from datetime import UTC, datetime, timedelta

from db import (
    add_message,
    get_client,
    get_history,
    list_active_workspaces,
    log_event,
    set_stage,
    upsert_lead,
)
from dotenv import load_dotenv
from intelligence import bant_score, split_reply_and_meta
from run_sdr import generate_reply, send_whatsapp
from utils import strip_control_blocks
from workspace_context import WorkspaceContext, resolve_workspace

load_dotenv()

ELIGIBLE_STAGES = ("sdr", "qualified", "closer", "followup")


def list_stale_leads(workspace_id: str, days: int, limit: int = 50) -> list[dict]:
    cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
    result = (
        get_client()
        .table("leads")
        .select(
            "id, phone, name, company, stage, last_message_at, metadata, workspace_id, bant"
        )
        .eq("workspace_id", workspace_id)
        .in_("stage", list(ELIGIBLE_STAGES))
        .lt("last_message_at", cutoff)
        .order("last_message_at", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data or []


def recent_followup_event(lead_id: str, hours: int) -> bool:
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
    """Pedido interno ao modelo com memoria rica do lead."""
    bant = lead.get("bant") or {}
    parts = [
        "Gere UMA mensagem curta de follow-up no WhatsApp (2-4 linhas).",
        "Nao diga apenas 'ainda tem interesse?'. Use o contexto abaixo.",
        f"Estagio: {lead.get('stage') or 'sdr'}",
    ]
    if lead.get("name"):
        parts.append(f"Nome: {lead['name']}")
    if lead.get("company"):
        parts.append(f"Empresa: {lead['company']}")
    if bant:
        parts.append(f"BANT: {bant} (score={bant_score(bant)})")
    user_bits = [h["content"] for h in history if h.get("role") == "user"][-3:]
    if user_bits:
        parts.append("Ultimas mensagens do lead:")
        for bit in user_bits:
            parts.append(f"  - {bit[:200]}")
    parts.append(
        "Lembre a dor ou o tema em 1 linha e proponha 1 proximo passo claro. "
        "Inclua o bloco ---META--- no final conforme o protocolo."
    )
    return "\n".join(parts)


def process_lead(ws: WorkspaceContext, lead: dict, dry_run: bool = False) -> dict:
    lead_id = lead["id"]
    phone = lead["phone"]
    stage = lead.get("stage") or "sdr"

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
        send_whatsapp(ws, phone, reply)
        log_event("followup_sent", {"phone": phone}, lead_id=lead_id, workspace_id=ws.id)
        return {"phone": phone, "workspace": ws.slug, "status": "sent"}
    except Exception as exc:
        log_event(
            "followup_send_error",
            {"error": str(exc)},
            lead_id=lead_id,
            workspace_id=ws.id,
        )
        return {"phone": phone, "workspace": ws.slug, "status": "error", "error": str(exc)}


def run_for_workspace(ws: WorkspaceContext, limit: int = 50, dry_run: bool = False) -> list[dict]:
    leads = list_stale_leads(ws.id, days=ws.followup_stale_days, limit=limit)
    print(f"[{ws.slug}] dias={ws.followup_stale_days} candidatos={len(leads)} dry_run={dry_run}")
    results = []
    for lead in leads:
        result = process_lead(ws, lead, dry_run=dry_run)
        results.append(result)
        print(f"  {result.get('phone')}: {result.get('status')} {result.get('reason') or ''}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="ForceIA Follow-up Job multi-tenant")
    parser.add_argument("--workspace", type=str, help="Slug do workspace")
    parser.add_argument("--all", action="store_true", help="Todos os workspaces ativos")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workspaces: list[WorkspaceContext] = []
    if args.all:
        for row in list_active_workspaces():
            workspaces.append(WorkspaceContext.from_row(row))
    else:
        slug = args.workspace or os.getenv("DEFAULT_WORKSPACE_SLUG", "default")
        ws = resolve_workspace(slug=slug)
        if not ws:
            print(f"Workspace '{slug}' nao encontrado")
            return
        workspaces = [ws]

    for ws in workspaces:
        run_for_workspace(ws, limit=args.limit, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
