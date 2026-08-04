"""Agendamento de reuniões via Google Calendar / Outlook (Composio)."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

log = logging.getLogger("forceia.integrations.calendar")

GOOGLE_CREATE = os.getenv(
    "FORCEIA_TOOL_GCAL_CREATE", "GOOGLECALENDAR_CREATE_EVENT"
)
OUTLOOK_CREATE = os.getenv(
    "FORCEIA_TOOL_OUTLOOK_CREATE", "OUTLOOK_CREATE_EVENT"
)


def _parse_start(start: str, tz_name: str = "America/Sao_Paulo") -> datetime:
    raw = (start or "").strip()
    if not raw:
        raise ValueError("start vazio")
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError as e:
        raise ValueError(f"start ISO inválido: {start}") from e
    if dt.tzinfo is None:
        try:
            dt = dt.replace(tzinfo=ZoneInfo(tz_name))
        except Exception:
            dt = dt.replace(tzinfo=timezone(timedelta(hours=-3)))
    return dt


def schedule_meeting(
    workspace_id: str,
    *,
    title: str,
    start: str,
    duration_minutes: int = 30,
    timezone_name: str = "America/Sao_Paulo",
    attendee_email: str | None = None,
    description: str | None = None,
    toolkit: str | None = None,
) -> dict[str, Any]:
    from integrations.composio_client import execute_tool, is_composio_enabled, list_connected

    if not is_composio_enabled():
        return {
            "success": False,
            "provider": "composio",
            "error": "composio_disabled",
            "dry_run": True,
        }

    try:
        start_dt = _parse_start(start, timezone_name)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    minutes = max(15, min(int(duration_minutes or 30), 240))
    end_dt = start_dt + timedelta(minutes=minutes)

    connected = {c.toolkit.lower() for c in list_connected(workspace_id)}
    preferred = (toolkit or "").lower().strip()
    if preferred in connected:
        use = preferred
    elif "googlecalendar" in connected:
        use = "googlecalendar"
    elif "outlook" in connected:
        use = "outlook"
    else:
        return {
            "success": False,
            "error": "calendar_not_connected",
            "hint": "Conecte googlecalendar ou outlook no painel de integrações",
            "connected": sorted(connected),
        }

    tool = GOOGLE_CREATE if use == "googlecalendar" else OUTLOOK_CREATE
    args: dict[str, Any] = {
        "summary": title or "Reunião ForceIA",
        "start_datetime": start_dt.isoformat(),
        "end_datetime": end_dt.isoformat(),
        "timezone": timezone_name,
        "description": description or "Reunião agendada pelo Closer ForceIA",
    }
    if attendee_email:
        args["attendees"] = [attendee_email]

    args_alt = {
        **args,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone_name},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": timezone_name},
    }

    result = execute_tool(workspace_id, tool, args)
    if not result.get("success"):
        result = execute_tool(workspace_id, tool, args_alt)

    out: dict[str, Any] = {
        "success": bool(result.get("success")),
        "provider": "composio",
        "toolkit": use,
        "tool": tool,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "title": title,
    }
    data = result.get("data") or {}
    if isinstance(data, dict):
        nested = data.get("data") if isinstance(data.get("data"), dict) else {}
        out["event_id"] = data.get("id") or data.get("event_id") or nested.get("id")
        out["html_link"] = data.get("htmlLink") or data.get("html_link")
        out["raw"] = data
    if not out["success"]:
        out["error"] = result.get("error") or "calendar_create_failed"
        log.warning("schedule_meeting falhou workspace=%s: %s", workspace_id, out["error"])
    else:
        log.info("meeting scheduled workspace=%s start=%s tool=%s", workspace_id, out["start"], tool)
    return out
