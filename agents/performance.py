"""
ForceIA — Métricas de performance do time de vendas (IA vs humano).

Responde perguntas do tipo:
  "Seu SDR agendou X reuniões esta semana"
  "A IA fechou Y% mais qualificações que o atendimento manual"
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        s = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except Exception:
        return None


def period_bounds(period: str = "week") -> tuple[datetime, datetime, str]:
    """Retorna (start, end, label) em UTC."""
    now = datetime.now(UTC)
    p = (period or "week").strip().lower()
    if p in ("day", "hoje", "today"):
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        label = "hoje"
    elif p in ("month", "mes", "mês"):
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        label = "este mês"
    else:
        # semana corrente (segunda 00:00 UTC)
        start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        label = "esta semana"
    return start, now, label


def _in_period(ts: str | None, start: datetime, end: datetime) -> bool:
    dt = _parse_ts(ts)
    if not dt:
        return False
    return start <= dt <= end


def _is_human_event(ev: dict) -> bool:
    payload = ev.get("payload") or {}
    source = str(payload.get("source") or "").lower()
    etype = str(ev.get("type") or "").lower()
    if source in ("admin", "human", "console", "manual"):
        return True
    if etype in ("agent_paused", "agent_resumed", "internal_note"):
        return True
    if payload.get("by") and source != "ai":
        # ações com autor humano no console
        if etype in ("stage_changed", "meeting_scheduled", "proposal_generated"):
            return source == "admin" or bool(payload.get("by"))
    return False


def compute_performance(
    *,
    workspace_id: str,
    events: list[dict] | None = None,
    leads: list[dict] | None = None,
    period: str = "week",
) -> dict[str, Any]:
    """
    Agrega KPIs do período.

    Preferência: events do workspace. Fallback leve em metadata dos leads.
    """
    start, end, label = period_bounds(period)
    events = events or []
    leads = leads or []

    period_events = [e for e in events if _in_period(e.get("created_at"), start, end)]

    meetings_ai = 0
    meetings_human = 0
    qualified_ai = 0
    qualified_human = 0
    won_ai = 0
    won_human = 0
    proposals_ai = 0
    proposals_human = 0
    messages_ai = 0  # proxy via eventos message_processed / agent replies
    handoffs = 0
    pauses = 0

    for ev in period_events:
        etype = str(ev.get("type") or "").lower()
        payload = ev.get("payload") or {}
        human = _is_human_event(ev)

        if etype in ("meeting_scheduled", "meeting_booked", "calendar_event"):
            if human:
                meetings_human += 1
            else:
                meetings_ai += 1
        elif etype == "stage_changed":
            to = str(payload.get("to") or "").lower()
            if to in ("qualified", "closer"):
                if human:
                    qualified_human += 1
                else:
                    qualified_ai += 1
            if to == "won":
                if human:
                    won_human += 1
                else:
                    won_ai += 1
        elif etype in ("proposal_generated", "proposal_sent"):
            if human:
                proposals_human += 1
            else:
                proposals_ai += 1
        elif etype == "message_processed":
            messages_ai += 1
        elif etype == "handoff_requested":
            handoffs += 1
        elif etype == "agent_paused":
            pauses += 1

    # Fallback: leads com last_meeting no período (metadata)
    if meetings_ai + meetings_human == 0 and leads:
        for lead in leads:
            meta = lead.get("metadata") or {}
            last = meta.get("last_meeting") or {}
            ts = last.get("at") or last.get("start") or lead.get("updated_at")
            if not _in_period(str(ts) if ts else None, start, end):
                continue
            if last:
                meetings_ai += 1

    meetings_total = meetings_ai + meetings_human
    qualified_total = qualified_ai + qualified_human
    won_total = won_ai + won_human

    def share(part: int, total: int) -> float:
        return round(part / total, 3) if total else 0.0

    headline = _build_headline(
        meetings_ai=meetings_ai,
        meetings_total=meetings_total,
        qualified_ai=qualified_ai,
        won_ai=won_ai,
        label=label,
    )

    return {
        "period": period,
        "period_label": label,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "headline": headline,
        "meetings": {
            "total": meetings_total,
            "ai": meetings_ai,
            "human": meetings_human,
            "ai_share": share(meetings_ai, meetings_total),
        },
        "qualified": {
            "total": qualified_total,
            "ai": qualified_ai,
            "human": qualified_human,
            "ai_share": share(qualified_ai, qualified_total),
        },
        "won": {
            "total": won_total,
            "ai": won_ai,
            "human": won_human,
            "ai_share": share(won_ai, won_total),
        },
        "proposals": {
            "total": proposals_ai + proposals_human,
            "ai": proposals_ai,
            "human": proposals_human,
        },
        "activity": {
            "messages_processed": messages_ai,
            "handoffs": handoffs,
            "human_takeovers": pauses,
        },
        "comparison": {
            "ai_vs_human_meetings": meetings_ai - meetings_human,
            "ai_vs_human_qualified": qualified_ai - qualified_human,
            "ai_vs_human_won": won_ai - won_human,
        },
    }


def _build_headline(
    *,
    meetings_ai: int,
    meetings_total: int,
    qualified_ai: int,
    won_ai: int,
    label: str,
) -> str:
    if meetings_ai > 0:
        return f"Seu SDR de IA agendou {meetings_ai} reunião{'ões' if meetings_ai != 1 else ''} {label}"
    if meetings_total > 0:
        return f"Seu time agendou {meetings_total} reunião{'ões' if meetings_total != 1 else ''} {label}"
    if qualified_ai > 0:
        return f"Seu SDR qualificou {qualified_ai} lead{'s' if qualified_ai != 1 else ''} {label}"
    if won_ai > 0:
        return f"Seu Closer de IA fechou {won_ai} negócio{'s' if won_ai != 1 else ''} {label}"
    return f"Seu time de IA está ativo — ainda sem reuniões registradas {label}"


def fetch_performance(workspace_id: str, period: str = "week", events_limit: int = 500) -> dict[str, Any]:
    """Carrega events/leads do DB e calcula performance."""
    from db import list_leads, list_recent_events

    events = list_recent_events(workspace_id, limit=events_limit)
    leads = list_leads(workspace_id, limit=200)
    return compute_performance(
        workspace_id=workspace_id,
        events=events,
        leads=leads,
        period=period,
    )
