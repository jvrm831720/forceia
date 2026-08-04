"""
ForceIA — Score de lead em tempo real + ranking hot leads.

Score 0–100 composto por:
  BANT (0–40) | intent ready_to_buy (0–25) | enrichment (0–15)
  engagement (0–10) | stage (0–10)

Hot: score >= HOT_THRESHOLD ou intent == ready_to_buy.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

HOT_THRESHOLD = 70

_STAGE_BONUS = {
    "sdr": 2,
    "qualified": 6,
    "closer": 9,
    "followup": 4,
    "won": 10,
    "lost": 0,
}


def _parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    try:
        s = str(value).replace("Z", "+00:00")
        d = datetime.fromisoformat(s)
        return d if d.tzinfo else d.replace(tzinfo=UTC)
    except Exception:
        return None


def engagement_score(lead: dict, *, message_count: int | None = None) -> int:
    score = 0
    meta = lead.get("metadata") or {}
    count = message_count
    if count is None:
        count = int(meta.get("message_count") or meta.get("msg_count") or 0)
    if count >= 8:
        score += 5
    elif count >= 4:
        score += 3
    elif count >= 1:
        score += 1
    last = _parse_ts(lead.get("last_message_at") or lead.get("updated_at"))
    if last:
        hours = (datetime.now(UTC) - last).total_seconds() / 3600
        if hours <= 2:
            score += 5
        elif hours <= 24:
            score += 3
        elif hours <= 72:
            score += 1
    return min(10, score)


def enrichment_score(lead: dict) -> int:
    meta = lead.get("metadata") or {}
    enr = meta.get("enrichment") if isinstance(meta.get("enrichment"), dict) else {}
    score = 0
    if lead.get("name") or enr.get("name"):
        score += 4
    if lead.get("company") or enr.get("company"):
        score += 4
    if enr.get("title") or enr.get("role") or enr.get("job_title"):
        score += 4
    if enr.get("linkedin_url") or enr.get("linkedin"):
        score += 3
    return min(15, score)


def intent_score(lead: dict) -> int:
    meta = lead.get("metadata") or {}
    intent = (meta.get("buying_intent") or meta.get("intent_class") or "").lower()
    conf = float(meta.get("intent_confidence") or 0)
    if intent in ("ready_to_buy", "ready", "buying"):
        base = 25
    elif intent in ("evaluating", "considering"):
        base = 15
    elif intent in ("researching", "research", "curious"):
        base = 6
    elif intent in ("objection", "not_now", "lost_signal"):
        base = 2
    else:
        base = 0
    if conf > 0:
        base = int(round(base * (0.5 + 0.5 * min(1.0, conf))))
    return min(25, base)


def bant_component(lead: dict) -> int:
    from intelligence import bant_score

    return min(40, int(round(bant_score(lead.get("bant")) * 0.4)))


def stage_component(lead: dict) -> int:
    stage = (lead.get("stage") or "sdr").lower()
    return _STAGE_BONUS.get(stage, 0)


def compute_lead_score(lead: dict, *, message_count: int | None = None) -> dict[str, Any]:
    parts = {
        "bant": bant_component(lead),
        "intent": intent_score(lead),
        "enrichment": enrichment_score(lead),
        "engagement": engagement_score(lead, message_count=message_count),
        "stage": stage_component(lead),
    }
    total = max(0, min(100, sum(parts.values())))
    meta = lead.get("metadata") or {}
    intent = (meta.get("buying_intent") or "").lower()
    hot = total >= HOT_THRESHOLD or intent in ("ready_to_buy", "ready", "buying")
    tier = "hot" if hot else ("warm" if total >= 45 else "cold")
    return {
        "score": total,
        "parts": parts,
        "hot": hot,
        "tier": tier,
        "threshold": HOT_THRESHOLD,
    }


def apply_score_to_lead(lead: dict, score_info: dict[str, Any]) -> dict:
    out = dict(lead)
    bant = dict(out.get("bant") or {})
    bant["score"] = score_info["score"]
    out["bant"] = bant
    meta = dict(out.get("metadata") or {})
    meta["lead_score"] = score_info["score"]
    meta["lead_score_parts"] = score_info.get("parts")
    meta["lead_tier"] = score_info.get("tier")
    meta["is_hot"] = score_info.get("hot")
    meta["scored_at"] = datetime.now(UTC).isoformat()
    out["metadata"] = meta
    return out


def rank_hot_leads(
    leads: list[dict],
    *,
    limit: int = 20,
    min_score: int | None = None,
) -> list[dict]:
    threshold = min_score if min_score is not None else HOT_THRESHOLD
    ranked: list[dict] = []
    for lead in leads:
        info = compute_lead_score(lead)
        if not (info["hot"] or info["score"] >= threshold):
            continue
        ranked.append(
            {**lead, "_score": info["score"], "_tier": info["tier"], "_parts": info["parts"]}
        )
    ranked.sort(
        key=lambda r: (r.get("_score") or 0, r.get("last_message_at") or ""),
        reverse=True,
    )
    return ranked[:limit]
