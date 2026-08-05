"""
ForceIA Skills de elite — inspiradas em playbooks de prospecting de alto nível
(Amplemarket-style), adaptadas ao stack ForceIA (playbook, enrichment, WhatsApp).

P1: skills condicionais por stage / message_count / tier para evitar prompt bloat.
"""

from __future__ import annotations

from skills.hiring_signal import (
    analyze_hiring_signal,
    format_hiring_signal_for_prompt,
    hiring_signal_from_lead,
)
from skills.icp_fit import compute_icp_fit, format_icp_for_prompt
from skills.personalization import build_personalization_brief, format_personalization_for_prompt
from skills.pipeline_health import score_pipeline_lead, format_pipeline_for_prompt
from skills.pre_call import build_pre_call_brief, format_pre_call_for_prompt
from skills.revival import score_revival, format_revival_for_prompt

SKILL_CATALOG = [
    {
        "id": "enrich_and_score",
        "name": "Enrich & Score Lead",
        "description": "Enrichment + ICP fit score 1–100 com next actions",
        "module": "skills.icp_fit",
    },
    {
        "id": "outreach_personalization",
        "name": "Outreach Personalization",
        "description": "Ângulos de personalização + openers para o SDR",
        "module": "skills.personalization",
    },
    {
        "id": "pre_call_brief",
        "name": "Pre-Call Research Brief",
        "description": "Brief completo antes de reunião/closer",
        "module": "skills.pre_call",
    },
    {
        "id": "closed_lost_revival",
        "name": "Closed-Lost Revival",
        "description": "Score de revival + opener para leads lost",
        "module": "skills.revival",
    },
    {
        "id": "pipeline_health",
        "name": "Pipeline Account Health",
        "description": "Saúde do lead no funil + ação prioritária",
        "module": "skills.pipeline_health",
    },
    {
        "id": "hiring_signal_prospector",
        "name": "Hiring Signal Prospector",
        "description": "Vagas como intent: força do sinal, dor, opener para decision-maker",
        "module": "skills.hiring_signal",
    },
]


def list_skills() -> list[dict]:
    return list(SKILL_CATALOG)


def _message_count(lead: dict, messages: list[dict] | None) -> int:
    if messages is not None:
        return len(messages)
    meta = lead.get("metadata") or {}
    try:
        return int(meta.get("message_count") or meta.get("msg_count") or 0)
    except (TypeError, ValueError):
        return 0


def _tier(lead: dict) -> str:
    meta = lead.get("metadata") or {}
    return str(meta.get("lead_tier") or "").lower()


def build_skills_context(
    *,
    lead: dict,
    playbook: dict | None,
    agent: str = "sdr",
    messages: list[dict] | None = None,
) -> str:
    """Bloco único injetado no system prompt conforme agente/stage/contagem (P1)."""
    parts: list[str] = []
    stage = (lead.get("stage") or "sdr").lower()
    agent = (agent or "sdr").lower()
    msg_n = _message_count(lead, messages)
    tier = _tier(lead)
    early = msg_n <= 4

    # ICP: sempre no início; depois só se tier não for hot (reavaliar fit)
    if early or tier in ("", "cold", "warm"):
        icp = format_icp_for_prompt(lead, playbook)
        if icp:
            parts.append(icp)

    # Hiring signal: prioridade na abertura SDR
    if agent == "sdr" and stage in ("sdr", "qualified") and early:
        hiring = format_hiring_signal_for_prompt(lead, playbook)
        if hiring:
            parts.append(hiring)

    # Personalization: primeiras mensagens SDR/qualified
    if (agent == "sdr" or stage in ("sdr", "qualified")) and msg_n <= 6:
        pers = format_personalization_for_prompt(lead, playbook)
        if pers:
            parts.append(pers)

    # Pre-call: só closer / qualified avançado
    if agent == "closer" or stage in ("closer", "qualified"):
        brief = format_pre_call_for_prompt(lead, playbook, messages=messages)
        if brief:
            parts.append(brief)

    # Revival: followup / lost
    if agent == "followup" or stage in ("followup", "lost"):
        rev = format_revival_for_prompt(lead, playbook)
        if rev:
            parts.append(rev)

    # Pipeline health: se não está hot, ou followup, ou msg_n alta
    if tier != "hot" or stage in ("followup", "lost") or msg_n >= 8:
        health = format_pipeline_for_prompt(lead)
        if health:
            parts.append(health)

    return "\n\n".join(parts) if parts else ""


__all__ = [
    "SKILL_CATALOG",
    "list_skills",
    "build_skills_context",
    "compute_icp_fit",
    "build_personalization_brief",
    "build_pre_call_brief",
    "score_revival",
    "score_pipeline_lead",
    "analyze_hiring_signal",
    "hiring_signal_from_lead",
]
