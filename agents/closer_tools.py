"""ForceIA — Tools do Closer: Calendar real + proposta / link de pagamento."""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import quote, urlencode

log = logging.getLogger("forceia.closer_tools")


def _payment_base() -> str:
    return (os.getenv("FORCEIA_PAYMENT_BASE_URL") or os.getenv("FORCEIA_PROPOSAL_BASE_URL") or "").rstrip("/")


def _default_duration_min() -> int:
    try:
        return int(os.getenv("FORCEIA_MEETING_DURATION_MIN", "30"))
    except ValueError:
        return 30


def _calendar_tools() -> list[str]:
    raw = os.getenv(
        "FORCEIA_CALENDAR_TOOLS",
        "GOOGLECALENDAR_CREATE_EVENT,GOOGLECALENDAR_EVENTS_LIST,OUTLOOK_OUTLOOK_CALENDAR_CREATE_EVENT",
    )
    return [s.strip() for s in raw.split(",") if s.strip()]


def schedule_meeting(
    workspace_id: str,
    *,
    title: str,
    start_iso: str,
    end_iso: str | None = None,
    attendee_email: str | None = None,
    description: str | None = None,
    timezone: str = "America/Sao_Paulo",
) -> dict[str, Any]:
    if not end_iso:
        try:
            start = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
            end_iso = (start + timedelta(minutes=_default_duration_min())).isoformat()
        except Exception:
            end_iso = start_iso
    args = {
        "summary": title,
        "start_datetime": start_iso,
        "end_datetime": end_iso,
        "timezone": timezone,
        "description": description or "Reunião comercial ForceIA",
    }
    if attendee_email:
        args["attendees"] = [attendee_email]
        args["participant_email"] = attendee_email
    try:
        from integrations.composio_client import execute_tool, is_composio_enabled
        if is_composio_enabled():
            for tool in _calendar_tools():
                if "LIST" in tool.upper():
                    continue
                result = execute_tool(workspace_id, tool, args)
                if result.get("success"):
                    data = result.get("data") or {}
                    link = (
                        data.get("htmlLink")
                        or data.get("html_link")
                        or data.get("link")
                        or ((data.get("result") or {}).get("htmlLink") if isinstance(data.get("result"), dict) else None)
                    )
                    return {
                        "success": True,
                        "provider": "composio",
                        "tool": tool,
                        "event_link": link,
                        "start": start_iso,
                        "end": end_iso,
                        "data": data,
                    }
    except Exception as e:
        log.warning("schedule_meeting composio: %s", e)

    def _gcal_stamp(iso: str) -> str:
        try:
            d = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(UTC)
            return d.strftime("%Y%m%dT%H%M%SZ")
        except Exception:
            return ""

    dates = f"{_gcal_stamp(start_iso)}/{_gcal_stamp(end_iso)}"
    gcal = (
        "https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={quote(title)}&dates={dates}&details={quote(description or '')}"
    )
    return {
        "success": True,
        "provider": "gcal_template",
        "event_link": gcal,
        "start": start_iso,
        "end": end_iso,
        "message": "Composio indisponível — link template gerado",
    }


def generate_proposal_link(
    *,
    workspace_slug: str,
    lead: dict,
    playbook: dict | None = None,
    plan: str | None = None,
    amount: str | None = None,
) -> dict[str, Any]:
    playbook = playbook or {}
    pricing = playbook.get("pricing") if isinstance(playbook.get("pricing"), dict) else {}
    plan = plan or pricing.get("model") or "standard"
    amount = amount or pricing.get("range") or ""
    base = _payment_base()
    params = {
        "workspace": workspace_slug,
        "lead": lead.get("id") or "",
        "phone": lead.get("phone") or "",
        "plan": plan,
    }
    if amount:
        params["amount"] = amount
    url = None
    if base:
        sep = "&" if "?" in base else "?"
        url = f"{base}{sep}{urlencode({k: v for k, v in params.items() if v})}"
    notes = str(pricing.get("notes") or "")
    m = re.search(r"https?://\S+", notes)
    if not url and m:
        url = m.group(0).rstrip(".,)")
    summary_lines = [
        f"Proposta — {playbook.get('company_name') or workspace_slug}",
        f"Lead: {lead.get('name') or lead.get('phone') or '—'}",
    ]
    if lead.get("company"):
        summary_lines.append(f"Empresa: {lead['company']}")
    if plan:
        summary_lines.append(f"Plano: {plan}")
    if amount:
        summary_lines.append(f"Faixa: {amount}")
    if url:
        summary_lines.append(f"Link: {url}")
    return {
        "success": True,
        "url": url,
        "plan": plan,
        "amount": amount,
        "summary": "\n".join(summary_lines),
        "has_payment_link": bool(url),
    }


def parse_schedule_from_meta(meta: dict) -> dict[str, Any] | None:
    if not meta:
        return None
    if meta.get("schedule") and isinstance(meta["schedule"], dict):
        s = meta["schedule"]
        if s.get("start") or s.get("start_iso") or s.get("when"):
            return {
                "start_iso": s.get("start_iso") or s.get("start") or s.get("when"),
                "end_iso": s.get("end_iso") or s.get("end"),
                "title": s.get("title") or "Reunião comercial",
                "attendee_email": s.get("email") or s.get("attendee_email"),
            }
    if meta.get("calendar_request") or meta.get("schedule_meeting"):
        raw = meta.get("calendar_request") or meta.get("schedule_meeting")
        if isinstance(raw, dict):
            return {
                "start_iso": raw.get("start_iso") or raw.get("start") or raw.get("when"),
                "end_iso": raw.get("end_iso") or raw.get("end"),
                "title": raw.get("title") or "Reunião comercial",
                "attendee_email": raw.get("email"),
            }
        if isinstance(raw, str) and raw.strip():
            return {"start_iso": raw.strip(), "title": "Reunião comercial"}
    return None


def parse_proposal_from_meta(meta: dict) -> dict[str, Any] | None:
    if not meta:
        return None
    if meta.get("send_proposal") or meta.get("payment_link") or meta.get("proposal"):
        raw = meta.get("proposal") if isinstance(meta.get("proposal"), dict) else {}
        return {
            "plan": raw.get("plan") or meta.get("plan"),
            "amount": raw.get("amount") or meta.get("amount"),
            "requested": True,
        }
    return None


def execute_closer_actions(
    workspace_id: str,
    workspace_slug: str,
    lead: dict,
    meta: dict,
    playbook: dict | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {"calendar": None, "proposal": None, "notes_for_reply": []}
    sched = parse_schedule_from_meta(meta)
    if sched and sched.get("start_iso"):
        cal = schedule_meeting(
            workspace_id,
            title=sched.get("title") or f"Reunião — {lead.get('name') or lead.get('phone')}",
            start_iso=str(sched["start_iso"]),
            end_iso=sched.get("end_iso"),
            attendee_email=sched.get("attendee_email") or lead.get("email"),
            description=f"Lead {lead.get('phone')} | stage {lead.get('stage')}",
        )
        out["calendar"] = cal
        if cal.get("event_link"):
            out["notes_for_reply"].append(f"Link da reunião: {cal['event_link']}")
    prop_req = parse_proposal_from_meta(meta)
    if prop_req:
        prop = generate_proposal_link(
            workspace_slug=workspace_slug,
            lead=lead,
            playbook=playbook,
            plan=prop_req.get("plan"),
            amount=prop_req.get("amount"),
        )
        out["proposal"] = prop
        if prop.get("url"):
            out["notes_for_reply"].append(f"Link da proposta/pagamento: {prop['url']}")
        elif prop.get("summary"):
            out["notes_for_reply"].append(prop["summary"])
    return out
