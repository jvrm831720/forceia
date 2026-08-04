"""Envio de e-mail via Gmail / Outlook (Composio)."""

from __future__ import annotations

import logging
import os
from typing import Any

log = logging.getLogger("forceia.integrations.email")

GMAIL_SEND = os.getenv("FORCEIA_TOOL_GMAIL_SEND", "GMAIL_SEND_EMAIL")
OUTLOOK_SEND = os.getenv("FORCEIA_TOOL_OUTLOOK_SEND", "OUTLOOK_SEND_EMAIL")


def send_email(
    workspace_id: str,
    *,
    to: str,
    subject: str,
    body: str,
    toolkit: str | None = None,
) -> dict[str, Any]:
    from integrations.composio_client import execute_tool, is_composio_enabled, list_connected

    if not is_composio_enabled():
        return {"success": False, "error": "composio_disabled", "dry_run": True}

    to = (to or "").strip()
    if not to or "@" not in to:
        return {"success": False, "error": "invalid_recipient"}

    connected = {c.toolkit.lower() for c in list_connected(workspace_id)}
    preferred = (toolkit or "").lower().strip()
    if preferred in connected:
        use = preferred
    elif "gmail" in connected:
        use = "gmail"
    elif "outlook" in connected:
        use = "outlook"
    else:
        return {
            "success": False,
            "error": "email_not_connected",
            "hint": "Conecte gmail ou outlook no painel",
            "connected": sorted(connected),
        }

    tool = GMAIL_SEND if use == "gmail" else OUTLOOK_SEND
    args = {
        "to": to,
        "subject": subject or "ForceIA",
        "body": body or "",
        "recipient_email": to,
        "message_body": body or "",
    }
    result = execute_tool(workspace_id, tool, args)
    out = {
        "success": bool(result.get("success")),
        "provider": "composio",
        "toolkit": use,
        "tool": tool,
        "to": to,
    }
    if not out["success"]:
        out["error"] = result.get("error") or "email_send_failed"
        log.warning("send_email falhou: %s", out["error"])
    return out
