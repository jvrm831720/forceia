"""
ForceIA - Job de Follow-up

Busca leads parados no Supabase e dispara o agente de follow-up via WhatsApp.

Uso:
  python followup_job.py              # roda uma vez
  python followup_job.py --dry-run    # so lista, nao envia
  python followup_job.py --days 3     # considera parado apos 3 dias

Agende com cron, por exemplo a cada 6h:
  0 */6 * * * cd /path/to/forceia/agents && /path/to/venv/bin/python followup_job.py
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from db import get_client, get_history, log_event, set_stage, upsert_lead
from prompts import load_prompt
from run_sdr import generate_reply, send_whatsapp

load_dotenv()

# Estagios elegiveis para follow-up automatico
ELIGIBLE_STAGES = ("sdr", "qualified", "closer", "followup")

# Nao reenviar se ja houve follow-up recente (horas)
MIN_HOURS_BETWEEN_FOLLOWUPS = int(os.getenv("FOLLOWUP_MIN_HOURS", "48"))


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        # Supabase retorna ISO com Z ou +00:00
        v = value.replace("Z", "+00:00")
        return datetime.fromisoformat(v)
    except Exception:
        return None


def list_stale_leads(days: int, limit: int = 50) -> list[dict]:
    """Leads sem mensagem ha N dias, ainda em funil ativo."""
    client = get_client()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_iso = cutoff.isoformat()

    result = (
        client.table("leads")
        .select("id, phone, name, company, stage, last_message_at, metadata")
        .in_("stage", list(ELIGIBLE_STAGES))
        .lt("last_message_at", cutoff_iso)
        .order("last_message_at", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data or []


def last_assistant_was_followup(lead_id: str) -> bool:
    history = get_history(lead_id, limit=5)
    for row in reversed(history):
        if row.get("role") == "assistant":
            return (row.get("agent") or "") == "followup"
    return False


def recent_followup_event(lead_id: str, hours: int) -> bool:
    client = get_client()
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    result = (
        client.table("events")
        .select("id, created_at")
        .eq("lead_id", lead_id)
        .eq("type", "followup_sent")
        .gte("created_at", since)
        .limit(1)
        .execute()
    )
    return bool(result.data)


def build_followup_context(lead: dict) -> str:
    name = lead.get("name") or ""
    company = lead.get("company") or ""
    stage = lead.get("stage") or "sdr"
    parts = [
        "Contexto interno (nao repetir literalmente ao lead):",
        f"- Estagio atual: {stage}",
    ]
    if name:
        parts.append(f"- Nome: {name}")
    if company:
        parts.append(f"- Empresa: {company}")
    parts.append(
        "Gere UMA mensagem curta de follow-up no WhatsApp para reengajar. "
        "Sem cumprimentos longos. Ofereca valor ou um proximo passo claro."
    )
    return "\n".join(parts)


def process_lead(lead: dict, dry_run: bool = False) -> dict:
    lead_id = lead["id"]
    phone = lead["phone"]
    stage = lead.get("stage") or "sdr"

    if recent_followup_event(lead_id, MIN_HOURS_BETWEEN_FOLLOWUPS):
        return {"phone": phone, "status": "skipped", "reason": "followup_recente"}

    history_rows = get_history(lead_id, limit=12)
    history = [{"role": r["role"], "content": r["content"]} for r in history_rows]
    user_stub = build_followup_context(lead)

    # Forca prompt de follow-up
    reply = generate_reply("followup", history, user_stub)

    if dry_run:
        return {"phone": phone, "status": "dry_run", "reply": reply}

    # Marca stage followup se ainda nao estiver
    if stage != "followup":
        set_stage(phone, "followup")
        log_event(lead_id, "stage_changed", {"from": stage, "to": "followup", "source": "followup_job"})

    from db import add_message

    add_message(lead_id, "assistant", reply, agent="followup")
    upsert_lead(phone)

    try:
        send_whatsapp(phone, reply)
        log_event(lead_id, "followup_sent", {"phone": phone})
        return {"phone": phone, "status": "sent", "reply": reply}
    except Exception as exc:
        log_event(lead_id, "followup_send_error", {"error": str(exc)})
        return {"phone": phone, "status": "error", "error": str(exc)}


def run(days: int = 5, limit: int = 50, dry_run: bool = False) -> list[dict]:
    leads = list_stale_leads(days=days, limit=limit)
    results = []
    print(f"Follow-up job | dias={days} | candidatos={len(leads)} | dry_run={dry_run}")
    for lead in leads:
        result = process_lead(lead, dry_run=dry_run)
        results.append(result)
        print(f"  {result.get('phone')}: {result.get('status')} {result.get('reason') or ''}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="ForceIA Follow-up Job")
    parser.add_argument("--days", type=int, default=int(os.getenv("FOLLOWUP_STALE_DAYS", "5")), help="Dias sem mensagem para considerar parado")
    parser.add_argument("--limit", type=int, default=50, help="Max leads por execucao")
    parser.add_argument("--dry-run", action="store_true", help="Nao envia WhatsApp nem grava follow-up")
    args = parser.parse_args()
    run(days=args.days, limit=args.limit, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
