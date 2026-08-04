"""
ForceIA — Handoff humano suave.

Quando o agente pede handoff ou o humano assume:
1. Gera resumo executivo do lead (BANT, intent, objeções, últimas msgs)
2. Pausa o agente
3. Notifica o closer humano (WhatsApp owner/handoff_phone)
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any


def resolve_handoff_phone(workspace: dict, override: str | None = None) -> str | None:
    if override and override.strip():
        return _digits(override)
    meta = workspace.get("metadata") or {}
    for key in ("handoff_phone", "closer_phone", "owner_phone", "report_phone"):
        if meta.get(key):
            return _digits(str(meta[key]))
    env = (os.getenv("FORCEIA_HANDOFF_PHONE") or os.getenv("FORCEIA_OWNER_PHONE") or "").strip()
    return _digits(env) if env else None


def _digits(phone: str) -> str:
    return "".join(c for c in phone if c.isdigit())


def build_handoff_summary(
    *,
    lead: dict,
    messages: list[dict] | None = None,
    reason: str | None = None,
    workspace_name: str = "ForceIA",
) -> str:
    """Resumo curto para o closer humano (WhatsApp)."""
    name = lead.get("name") or "Lead"
    company = lead.get("company") or "—"
    phone = lead.get("phone") or "—"
    stage = lead.get("stage") or "sdr"
    bant = lead.get("bant") or {}
    meta = lead.get("metadata") or {}
    intent = meta.get("buying_intent") or meta.get("last_intent") or "—"
    objections = meta.get("objections") or []
    if isinstance(objections, str):
        objections = [objections]

    lines = [
        f"🔔 *Handoff — {workspace_name}*",
        "",
        f"*Lead:* {name}",
        f"*Empresa:* {company}",
        f"*WhatsApp:* {phone}",
        f"*Estágio:* {stage}",
        f"*Intent:* {intent}",
    ]
    if reason:
        lines.append(f"*Motivo:* {reason}")

    bant_bits = []
    for k in ("need", "authority", "budget", "timeline"):
        if bant.get(k):
            bant_bits.append(f"• {k}: {bant[k]}")
    if bant_bits:
        lines.append("")
        lines.append("*BANT*")
        lines.extend(bant_bits)

    if objections:
        lines.append("")
        lines.append("*Objeções:* " + "; ".join(str(o) for o in objections[-3:]))

    if messages:
        recent = messages[-4:]
        lines.append("")
        lines.append("*Últimas mensagens*")
        for m in recent:
            role = m.get("role") or "?"
            agent = m.get("agent") or ""
            prefix = "Lead" if role == "user" else (agent or "IA")
            content = (m.get("content") or "").strip()
            if "---META---" in content:
                content = content.split("---META---", 1)[0].strip()
            if len(content) > 160:
                content = content[:157] + "…"
            if content:
                lines.append(f"_{prefix}:_ {content}")

    lines.extend(
        [
            "",
            "_Agente pausado — você assume a conversa._",
            f"_{datetime.now(UTC).strftime('%d/%m %H:%M')} UTC_",
        ]
    )
    return "\n".join(lines)


def execute_handoff(
    *,
    workspace: dict,
    lead: dict,
    reason: str | None = None,
    notify: bool = True,
    phone_override: str | None = None,
    by: str = "agent",
) -> dict[str, Any]:
    """Pausa agente, grava resumo, notifica humano."""
    from db import (
        get_messages_for_lead,
        log_event,
        merge_metadata,
        set_agent_paused,
        update_lead_fields,
    )
    from workspace_context import WorkspaceContext

    ws_id = workspace["id"]
    lead_id = lead["id"]
    msgs = get_messages_for_lead(lead_id, limit=30) if lead_id else []
    summary = build_handoff_summary(
        lead=lead,
        messages=msgs,
        reason=reason,
        workspace_name=workspace.get("name") or workspace.get("slug") or "ForceIA",
    )

    # Pausa
    updated = set_agent_paused(
        ws_id,
        lead_id,
        True,
        by=by,
        reason=reason or "handoff",
    )

    # Espelha resumo no metadata
    phone = lead.get("phone")
    handoff_payload = {
        "summary": summary,
        "reason": reason,
        "at": datetime.now(UTC).isoformat(),
        "by": by,
    }
    if phone:
        merge_metadata(ws_id, phone, {"last_handoff": handoff_payload, "handoff_requested": True})
    else:
        meta = dict((updated or lead).get("metadata") or {})
        meta["last_handoff"] = handoff_payload
        meta["handoff_requested"] = True
        update_lead_fields(ws_id, lead_id, metadata=meta)

    log_event(
        "handoff_executed",
        {"reason": reason, "by": by, "notified": False},
        lead_id=lead_id,
        workspace_id=ws_id,
    )

    result: dict[str, Any] = {
        "ok": True,
        "summary": summary,
        "agent_paused": True,
        "notified": False,
        "notify_phone": None,
    }

    if not notify:
        return result

    target = resolve_handoff_phone(workspace, phone_override)
    result["notify_phone"] = target
    if not target:
        result["message"] = "Sem handoff_phone / owner_phone configurado"
        return result

    try:
        from run_sdr import send_whatsapp

        ws_ctx = WorkspaceContext.from_row(workspace)
        send_whatsapp(ws_ctx, target, summary)
        result["notified"] = True
        log_event(
            "handoff_notified",
            {"phone": target, "reason": reason},
            lead_id=lead_id,
            workspace_id=ws_id,
        )
    except Exception as exc:
        result["error"] = str(exc)
        log_event(
            "handoff_notify_error",
            {"error": str(exc)},
            lead_id=lead_id,
            workspace_id=ws_id,
        )
    return result
