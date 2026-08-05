"""
ForceIA P2 — Badges de inteligência por lead (score, ICP, health, intent).

Usado no console admin e nas APIs de lista/métricas.
"""

from __future__ import annotations

from typing import Any


def build_lead_badges(
    lead: dict,
    *,
    playbook: dict | None = None,
    include_breakdown: bool = False,
) -> dict[str, Any]:
    """Pacote compacto de badges para UI / API."""
    meta = lead.get("metadata") or {}

    # Lead score (nativo)
    try:
        from lead_score import compute_lead_score

        score_info = compute_lead_score(lead)
    except Exception:
        score_info = {
            "score": meta.get("lead_score") or 0,
            "tier": meta.get("lead_tier") or "cold",
            "hot": bool(meta.get("is_hot")),
            "parts": meta.get("lead_score_parts") or {},
        }

    # ICP fit
    try:
        from skills.icp_fit import compute_icp_fit

        icp = compute_icp_fit(lead, playbook)
    except Exception:
        icp = {"score": 0, "grade": "?", "priority": "—"}

    # Pipeline health
    try:
        from skills.pipeline_health import score_pipeline_lead

        health = score_pipeline_lead(lead)
    except Exception:
        health = {"health": 0, "tier": "Cold", "action": "—"}

    intent = meta.get("buying_intent") or meta.get("last_intent") or "unknown"
    try:
        from intent import intent_label_pt

        intent_label = intent_label_pt(intent)
    except Exception:
        intent_label = str(intent)

    badges: dict[str, Any] = {
        "score": int(score_info.get("score") or 0),
        "score_tier": str(score_info.get("tier") or "cold"),
        "hot": bool(score_info.get("hot")),
        "icp_score": int(icp.get("score") or 0),
        "icp_grade": str(icp.get("grade") or "?"),
        "health": int(health.get("health") or 0),
        "health_tier": str(health.get("tier") or "Cold"),
        "health_action": str(health.get("action") or ""),
        "intent": str(intent),
        "intent_label": intent_label,
        "intent_confidence": meta.get("intent_confidence"),
    }
    if include_breakdown:
        badges["score_parts"] = score_info.get("parts") or {}
        badges["icp_priority"] = icp.get("priority")
        badges["icp_breakdown"] = icp.get("breakdown")
        badges["health_parts"] = health.get("parts") or {}
    return badges


def enrich_lead_row(lead: dict, playbook: dict | None = None) -> dict[str, Any]:
    """Lead list row + badges (sem payload pesado)."""
    b = build_lead_badges(lead, playbook=playbook, include_breakdown=False)
    return {
        "id": lead.get("id"),
        "phone": lead.get("phone"),
        "name": lead.get("name"),
        "company": lead.get("company"),
        "email": lead.get("email"),
        "stage": lead.get("stage"),
        "last_message_at": lead.get("last_message_at"),
        "updated_at": lead.get("updated_at"),
        "badges": b,
    }


def summarize_workspace_intelligence(leads: list[dict], playbook: dict | None = None) -> dict[str, Any]:
    """Agregados para KPIs do overview (hot / at-risk / intent)."""
    hot = 0
    at_risk = 0
    ready = 0
    grades: dict[str, int] = {}
    for lead in leads:
        b = build_lead_badges(lead, playbook=playbook)
        if b.get("hot") or b.get("score_tier") == "hot" or b.get("health_tier") == "Hot":
            hot += 1
        if b.get("health_tier") == "At Risk":
            at_risk += 1
        if str(b.get("intent") or "").lower() in ("ready_to_buy", "ready"):
            ready += 1
        g = str(b.get("icp_grade") or "?")
        grades[g] = grades.get(g, 0) + 1
    return {
        "hot_count": hot,
        "at_risk_count": at_risk,
        "ready_to_buy_count": ready,
        "icp_grades": grades,
        "sampled": len(leads),
    }
