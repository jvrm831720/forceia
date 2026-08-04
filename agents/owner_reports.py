"""
ForceIA — Relatórios no WhatsApp para o dono do negócio.

Gera texto curto estilo WhatsApp com performance da semana e envia
para o telefone configurado em workspaces.metadata.owner_phone.
"""

from __future__ import annotations

import os
from typing import Any


def format_owner_report(
    *,
    workspace_name: str,
    performance: dict[str, Any],
    metrics: dict[str, Any] | None = None,
) -> str:
    """Monta mensagem PT-BR pronta para WhatsApp."""
    name = workspace_name or "ForceIA"
    label = performance.get("period_label") or "esta semana"
    meetings = performance.get("meetings") or {}
    qualified = performance.get("qualified") or {}
    won = performance.get("won") or {}
    activity = performance.get("activity") or {}
    headline = performance.get("headline") or ""

    total_leads = (metrics or {}).get("total")
    win_rate = (metrics or {}).get("win_rate")
    by_stage = (metrics or {}).get("by_stage") or {}

    lines = [
        f"📊 *ForceIA — Relatório {label}*",
        f"*{name}*",
        "",
        f"✨ {headline}",
        "",
        "*Reuniões agendadas*",
        f"• Total: {meetings.get('total', 0)}",
        f"• IA: {meetings.get('ai', 0)}  ·  Humano: {meetings.get('human', 0)}",
        "",
        "*Qualificações*",
        f"• IA: {qualified.get('ai', 0)}  ·  Humano: {qualified.get('human', 0)}",
        "",
        "*Fechamentos (won)*",
        f"• IA: {won.get('ai', 0)}  ·  Humano: {won.get('human', 0)}",
    ]

    if total_leads is not None:
        lines.extend(
            [
                "",
                "*Pipeline*",
                f"• Leads totais: {total_leads}",
                f"• Em closer: {by_stage.get('closer', 0)}",
                f"• Win rate: {int(round((win_rate or 0) * 100))}%",
            ]
        )

    lines.extend(
        [
            "",
            "*Atividade*",
            f"• Msgs processadas: {activity.get('messages_processed', 0)}",
            f"• Handoffs: {activity.get('handoffs', 0)}",
            f"• Takeovers humanos: {activity.get('human_takeovers', 0)}",
            "",
            "_Seu time de vendas de IA — ForceIA_",
        ]
    )
    return "\n".join(lines)


def resolve_owner_phone(workspace: dict, override: str | None = None) -> str | None:
    if override and override.strip():
        return _digits(override)
    meta = workspace.get("metadata") or {}
    phone = meta.get("owner_phone") or meta.get("report_phone") or meta.get("owner_whatsapp")
    if phone:
        return _digits(str(phone))
    env = (os.getenv("FORCEIA_OWNER_PHONE") or "").strip()
    return _digits(env) if env else None


def _digits(phone: str) -> str:
    return "".join(c for c in phone if c.isdigit())


def build_and_send_owner_report(
    *,
    workspace: dict,
    period: str = "week",
    phone: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Gera relatório + envia via Evolution (ou só preview)."""
    from db import count_leads_by_stage, log_event
    from performance import fetch_performance
    from state_machine import STAGES
    from workspace_context import WorkspaceContext

    ws_id = workspace["id"]
    perf = fetch_performance(ws_id, period=period)
    counts = count_leads_by_stage(ws_id)
    ordered = {stage: counts.get(stage, 0) for stage in STAGES}
    total = sum(ordered.values())
    won = ordered.get("won", 0)
    closed = won + ordered.get("lost", 0)
    metrics = {
        "total": total,
        "by_stage": ordered,
        "win_rate": round(won / closed, 3) if closed else 0.0,
    }
    text = format_owner_report(
        workspace_name=workspace.get("name") or workspace.get("slug") or "ForceIA",
        performance=perf,
        metrics=metrics,
    )
    target = resolve_owner_phone(workspace, phone)
    result: dict[str, Any] = {
        "text": text,
        "phone": target,
        "period": period,
        "performance": perf,
        "sent": False,
        "dry_run": dry_run,
    }

    if dry_run or not target:
        if not target:
            result["message"] = (
                "Defina metadata.owner_phone no workspace ou passe phone= no body"
            )
        return result

    ws_ctx = WorkspaceContext.from_row(workspace)
    from run_sdr import send_whatsapp

    try:
        send_whatsapp(ws_ctx, target, text)
        result["sent"] = True
        log_event(
            "owner_report_sent",
            {"phone": target, "period": period, "chars": len(text)},
            workspace_id=ws_id,
        )
    except Exception as exc:
        result["error"] = str(exc)
        log_event(
            "owner_report_error",
            {"phone": target, "error": str(exc)},
            workspace_id=ws_id,
        )
    return result
