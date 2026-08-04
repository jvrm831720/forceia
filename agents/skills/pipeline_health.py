"""
Skill: Pipeline Account Review (por lead).

Health 1–10 + tier Hot/Warm/Cold/At Risk + ação.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def _days_since(value: str | None) -> int | None:
    if not value:
        return None
    try:
        s = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return max(0, (datetime.now(UTC) - dt.astimezone(UTC)).days)
    except Exception:
        return None


def score_pipeline_lead(lead: dict) -> dict[str, Any]:
    stage = (lead.get("stage") or "sdr").lower()
    meta = lead.get("metadata") or {}
    days = _days_since(lead.get("last_message_at") or lead.get("updated_at"))

    # Engagement recency (0–3)
    if days is None:
        rec = 0
    elif days <= 3:
        rec = 3
    elif days <= 14:
        rec = 2
    elif days <= 45:
        rec = 1
    else:
        rec = 0

    # Depth (0–3): intent / bant / pause
    depth = 0
    bant = lead.get("bant") or {}
    filled = sum(1 for k in ("need", "authority", "budget", "timeline") if bant.get(k))
    if filled >= 3:
        depth = 3
    elif filled >= 1:
        depth = 2
    elif meta.get("last_intent") or meta.get("buying_intent"):
        depth = 1

    # Coverage proxy (0–2): enrichment + name/company
    cov = 0
    if lead.get("name") and lead.get("company"):
        cov = 2
    elif lead.get("name") or lead.get("company"):
        cov = 1

    # Stage (0–2)
    stage_pts = {
        "won": 2,
        "closer": 2,
        "qualified": 2,
        "followup": 1,
        "sdr": 1,
        "lost": 0,
    }.get(stage, 0)

    total = rec + depth + cov + stage_pts  # max 10

    if stage == "lost" and (days or 99) > 30:
        tier = "Cold"
    elif total >= 8:
        tier = "Hot"
    elif total >= 5:
        tier = "Warm"
    elif stage in ("qualified", "closer") and rec == 0:
        tier = "At Risk"
    else:
        tier = "Cold"

    actions = {
        "Hot": "Avançar: CTA claro ou agenda",
        "Warm": "Reengajar + completar BANT faltante",
        "Cold": "Reavaliar fit ou 1 toque de valor e parar",
        "At Risk": "URGENTE: breakup ou handoff humano",
    }

    return {
        "health": total,
        "tier": tier,
        "days_since_activity": days,
        "parts": {"recency": rec, "depth": depth, "coverage": cov, "stage": stage_pts},
        "action": actions.get(tier, "Revisar"),
    }


def format_pipeline_for_prompt(lead: dict) -> str:
    info = score_pipeline_lead(lead)
    return (
        f"## Pipeline health (skill)\n"
        f"Health {info['health']}/10 · tier **{info['tier']}** · "
        f"ação: {info['action']}"
        + (f" · silêncio há {info['days_since_activity']}d" if info.get("days_since_activity") is not None else "")
    )
