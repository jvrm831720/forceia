"""
ForceIA Skills de elite — inspiradas em playbooks de prospecting de alto nível
(Amplemarket-style), adaptadas ao stack ForceIA (playbook, enrichment, WhatsApp).

Não dependem de Amplemarket MCP. Usam playbook do workspace + enrichment +
mensagens + score nativo.
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


def build_skills_context(
    *,
    lead: dict,
    playbook: dict | None,
    agent: str = "sdr",
    messages: list[dict] | None = None,
) -> str:
    """Bloco único injetado no system prompt conforme o agente/stage."""
    parts: list[str] = []
    stage = (lead.get("stage") or "sdr").lower()

    icp = format_icp_for_prompt(lead, playbook)
    if icp:
        parts.append(icp)

    # Hiring signal tem prioridade alta na abertura do SDR
    hiring = format_hiring_signal_for_prompt(lead, playbook)
    if hiring:
        parts.append(hiring)

    if agent == "sdr" or stage in ("sdr", "qualified"):
        pers = format_personalization_for_prompt(lead, playbook)
        if pers:
            parts.append(pers)

    if agent == "closer" or stage in ("closer", "qualified"):
        brief = format_pre_call_for_prompt(lead, playbook, messages=messages)
        if brief:
            parts.append(brief)

    if agent == "followup" or stage in ("followup", "lost"):
        rev = format_revival_for_prompt(lead, playbook)
        if rev:
            parts.append(rev)

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
