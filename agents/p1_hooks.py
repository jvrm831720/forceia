"""P1 hooks for graph nodes — intent routing, turn policy, objection handoff."""

from __future__ import annotations

from typing import Any


def route_agent_by_intent(stage: str, agent: str, intent_info: dict, score_info: dict) -> str:
    intent_name = (intent_info.get("intent") or "").lower()
    if intent_name == "ready_to_buy":
        if stage in ("qualified", "closer"):
            return "closer"
        if stage == "sdr" and score_info.get("score", 0) >= 55:
            return "closer"
    elif intent_name == "objection":
        if stage in ("qualified", "closer"):
            return "closer"
    elif intent_name == "researching" and stage == "sdr":
        return "sdr"
    return agent


def apply_turn_policy_to_reply(reply: str, stage: str, agent: str) -> tuple[str, list[str]]:
    events: list[str] = []
    try:
        from turn_policy import enforce_turn_policy

        policy = enforce_turn_policy(reply, stage=stage, agent=agent or "sdr")
        if policy.get("modified"):
            events.append("turn_policy_enforced")
            for iss in policy.get("issues") or []:
                events.append(f"turn_policy:{iss}")
            return policy["reply"], events
    except Exception:
        events.append("turn_policy_error")
    return reply, events


def maybe_set_handoff_from_objections(lead: dict, meta: dict) -> tuple[dict, list[str]]:
    events: list[str] = []
    meta = dict(meta or {})
    try:
        from turn_policy import should_handoff_on_objections

        if should_handoff_on_objections(lead, meta) and not meta.get("handoff"):
            meta["handoff"] = True
            events.append("handoff_from_objections")
    except Exception:
        pass
    return meta, events


def route_stage_by_intent(
    stage: str,
    new_stage: str,
    intent_info: dict,
    score_info: dict,
    can_transition,
) -> str:
    intent_name = (intent_info.get("intent") or "").lower()
    if intent_name == "ready_to_buy":
        conf = float(intent_info.get("confidence") or 0)
        if new_stage == "sdr" and can_transition("sdr", "qualified"):
            if conf >= 0.7 and score_info.get("score", 0) >= 50:
                new_stage = "qualified"
        if new_stage == "qualified" and can_transition("qualified", "closer"):
            if conf >= 0.85 or score_info.get("hot"):
                new_stage = "closer"
    return new_stage
