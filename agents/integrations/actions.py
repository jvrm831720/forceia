"""
Orquestra ações de integração a partir do META do agente.

Usado pelo nó LangGraph `actions` e pelo fluxo linear (run_sdr).
"""

from __future__ import annotations

import logging
import re
from typing import Any

log = logging.getLogger("forceia.integrations.actions")

SCHEDULE_INTENTS = {
    "schedule",
    "agendar",
    "meeting",
    "reuniao",
    "reunião",
    "demo",
    "call",
}


def _intent_is_schedule(meta: dict) -> bool:
    intent = str(meta.get("intent") or "").strip().lower()
    if intent in SCHEDULE_INTENTS:
        return True
    if meta.get("meeting") and isinstance(meta["meeting"], dict):
        return True
    notes = str(meta.get("notes") or "").lower()
    if any(k in notes for k in ("agendar", "reunião", "demo", "calendário", "calendar")):
        return bool(meta.get("meeting") or re.search(r"\d{1,2}[:h]\d{2}", notes))
    return False


def _extract_meeting(meta: dict, lead: dict) -> dict[str, Any] | None:
    m = meta.get("meeting") if isinstance(meta.get("meeting"), dict) else {}
    start = m.get("start") or m.get("start_datetime") or meta.get("meeting_start")
    if not start:
        return None
    title = (
        m.get("title")
        or m.get("summary")
        or meta.get("meeting_title")
        or f"Reunião ForceIA — {lead.get('name') or lead.get('company') or 'Lead'}"
    )
    duration = int(m.get("duration_minutes") or m.get("duration") or meta.get("duration_minutes") or 30)
    tz = m.get("timezone") or m.get("timeZone") or "America/Sao_Paulo"
    email = m.get("attendee_email") or lead.get("email") or meta.get("email")
    description = m.get("description") or meta.get("notes")
    return {
        "title": str(title)[:200],
        "start": str(start),
        "duration_minutes": duration,
        "timezone_name": tz,
        "attendee_email": email,
        "description": description,
    }


def run_agent_actions(
    *,
    workspace_id: str,
    agent: str,
    stage: str,
    meta: dict,
    lead: dict,
    visible_reply: str = "",
) -> dict[str, Any]:
    meta = meta or {}
    lead = lead or {}
    actions: list[dict[str, Any]] = []
    reply_parts: list[str] = []
    lead_meta: dict[str, Any] = {}

    if agent in ("closer", "sdr") and stage in ("closer", "qualified", "sdr", "won"):
        if _intent_is_schedule(meta):
            meeting = _extract_meeting(meta, lead)
            if meeting:
                from integrations.tools.calendar import schedule_meeting

                result = schedule_meeting(workspace_id, **meeting)
                actions.append({"type": "schedule_meeting", "result": result})
                if result.get("success"):
                    lead_meta["last_meeting"] = {
                        "title": meeting["title"],
                        "start": result.get("start") or meeting["start"],
                        "end": result.get("end"),
                        "event_id": result.get("event_id"),
                        "html_link": result.get("html_link"),
                        "toolkit": result.get("toolkit"),
                    }
                    when = result.get("start") or meeting["start"]
                    reply_parts.append(
                        f"✅ Reunião confirmada no calendário: *{meeting['title']}* em {when}."
                    )
                    if result.get("html_link"):
                        reply_parts.append(f"Link: {result['html_link']}")
                elif result.get("error") == "calendar_not_connected":
                    lead_meta["meeting_pending"] = meeting
                    reply_parts.append(
                        "Anotei o horário. Nosso time confirma o convite no calendário em seguida."
                    )
                elif result.get("error") == "composio_disabled":
                    lead_meta["meeting_pending"] = meeting
                    log.info("schedule dry-run (composio off): %s", meeting)
                else:
                    lead_meta["meeting_pending"] = meeting
                    log.warning("schedule failed: %s", result.get("error"))
            else:
                lead_meta["wants_meeting"] = True

    email = lead.get("email") or meta.get("email")
    last_meeting = lead_meta.get("last_meeting")
    if last_meeting and email and meta.get("send_email_confirmation"):
        from integrations.tools.email import send_email

        body = (
            f"Olá{' ' + (lead.get('name') or '')}!\n\n"
            f"Confirmamos nossa reunião: {last_meeting.get('title')}\n"
            f"Quando: {last_meeting.get('start')}\n"
        )
        if last_meeting.get("html_link"):
            body += f"Detalhes: {last_meeting['html_link']}\n"
        body += "\nAté lá,\nTime ForceIA"
        er = send_email(
            workspace_id,
            to=str(email),
            subject=f"Confirmação: {last_meeting.get('title')}",
            body=body,
        )
        actions.append({"type": "send_email", "result": er})

    if meta.get("handoff"):
        from integrations.tools.notify import notify_handoff

        reason = meta.get("notes") or meta.get("intent") or "handoff solicitado pelo agente"
        nr = notify_handoff(
            workspace_id,
            text=str(reason),
            lead_phone=lead.get("phone"),
            lead_name=lead.get("name"),
        )
        actions.append({"type": "notify_handoff", "result": nr})
        if nr.get("success"):
            lead_meta["handoff_notified"] = True

    suffix = "\n\n".join(reply_parts) if reply_parts else None
    return {
        "actions": actions,
        "reply_suffix": suffix,
        "lead_metadata": lead_meta,
    }
