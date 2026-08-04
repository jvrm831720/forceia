"""Notificações de handoff (Slack / Teams via Composio)."""

from __future__ import annotations

import logging
import os
from typing import Any

log = logging.getLogger("forceia.integrations.notify")

SLACK_SEND = os.getenv("FORCEIA_TOOL_SLACK_SEND", "SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL")
SLACK_SEND_ALT = os.getenv("FORCEIA_TOOL_SLACK_SEND_ALT", "SLACK_SEND_MESSAGE")


def notify_handoff(
    workspace_id: str,
    *,
    text: str,
    channel: str | None = None,
    lead_phone: str | None = None,
    lead_name: str | None = None,
) -> dict[str, Any]:
    from integrations.composio_client import execute_tool, is_composio_enabled, list_connected

    if not is_composio_enabled():
        return {"success": False, "error": "composio_disabled", "dry_run": True}

    connected = {c.toolkit.lower() for c in list_connected(workspace_id)}
    if "slack" not in connected:
        return {
            "success": False,
            "error": "slack_not_connected",
            "hint": "Conecte slack no painel de integrações",
        }

    channel = channel or os.getenv("FORCEIA_SLACK_CHANNEL", "#vendas")
    header = "🔔 *ForceIA — handoff humano*"
    lines = [header, text]
    if lead_name or lead_phone:
        lines.append(f"Lead: {lead_name or '—'} · {lead_phone or '—'}")
    message = "\n".join(lines)

    args = {"channel": channel, "text": message, "message": message}
    result = execute_tool(workspace_id, SLACK_SEND, args)
    if not result.get("success"):
        result = execute_tool(workspace_id, SLACK_SEND_ALT, args)

    out = {
        "success": bool(result.get("success")),
        "provider": "composio",
        "toolkit": "slack",
        "channel": channel,
    }
    if not out["success"]:
        out["error"] = result.get("error") or "slack_send_failed"
        log.warning("notify_handoff falhou: %s", out["error"])
    return out
