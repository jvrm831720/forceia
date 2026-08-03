"""ForceIA - Maquina de estados dos agentes."""

from __future__ import annotations

STAGES = ("sdr", "qualified", "closer", "followup", "won", "lost")

TRANSITIONS = {
    "sdr": {"qualified", "followup", "lost"},
    "qualified": {"closer", "followup", "lost"},
    "closer": {"won", "followup", "lost"},
    "followup": {"sdr", "qualified", "closer", "won", "lost"},
    "won": set(),
    "lost": {"sdr", "followup"},
}


def can_transition(current: str, target: str) -> bool:
    if current not in TRANSITIONS:
        return False
    return target in TRANSITIONS[current]


def next_agent_for_stage(stage: str) -> str:
    """Qual agente responde em cada estagio."""
    if stage in ("sdr",):
        return "sdr"
    if stage in ("qualified", "closer"):
        return "closer"
    if stage == "followup":
        return "followup"
    if stage == "won":
        return "closer"
    return "sdr"


def detect_stage_from_reply(reply: str, current: str) -> str:
    """
    Heuristica legada baseada em tags no texto.
    Preferir intelligence.stage_from_meta_or_tags em producao.
    """
    upper = (reply or "").upper()
    if "[QUALIFICADO]" in upper or "[QUALIFIED]" in upper:
        if can_transition(current, "qualified"):
            return "qualified"
        if can_transition(current, "closer"):
            return "closer"
    if "[WON]" in upper or "[FECHADO]" in upper:
        if can_transition(current, "won"):
            return "won"
    if "[LOST]" in upper or "[PERDIDO]" in upper:
        if can_transition(current, "lost"):
            return "lost"
    if "[FOLLOWUP]" in upper or "[FOLLOW-UP]" in upper:
        if can_transition(current, "followup"):
            return "followup"
    return current
