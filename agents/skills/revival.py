"""
Skill: Closed-Lost Revival Scanner (adaptado ao ForceIA).

Para leads em stage lost/followup: score de revival + opener de reengajamento.
"""

from __future__ import annotations

from datetime import UTC, datetime
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


def score_revival(lead: dict, playbook: dict | None = None) -> dict[str, Any]:
    stage = (lead.get("stage") or "").lower()
    meta = lead.get("metadata") or {}
    bant = lead.get("bant") or {}

    # Só faz sentido forte em lost/followup; ainda assim calculamos sempre
    reasons: list[str] = []
    priority = "Low"

    lost_reason = str(
        meta.get("lost_reason")
        or meta.get("close_reason")
        or meta.get("last_intent")
        or ""
    ).lower()

    # Timing/budget = melhor revival
    high_signals = ("timing", "prazo", "budget", "orçamento", "orcamento", "depois", "agora não", "agora nao")
    mid_signals = ("dark", "sumiu", "sem resposta", "no decision", "pesquisando")
    low_signals = ("não é fit", "nao e fit", "not a fit", "concorrente", "sem interesse")

    if any(s in lost_reason for s in high_signals) or bant.get("need"):
        priority = "High"
        reasons.append("Motivo de perda recuperável (timing/budget/need conhecido)")
    elif any(s in lost_reason for s in mid_signals):
        priority = "Medium"
        reasons.append("Went dark / sem decisão — vale reabordagem")
    elif any(s in lost_reason for s in low_signals):
        priority = "Low"
        reasons.append("Fit/concorrente — só se houver trigger externo")
    elif stage in ("lost", "followup"):
        priority = "Medium"
        reasons.append("Lead frio sem razão clara — teste reativação curta")

    months = None
    ts = _parse_ts(lead.get("updated_at") or lead.get("last_message_at"))
    if ts:
        months = max(0, int((datetime.now(UTC) - ts).days / 30))
        if months <= 3 and priority == "Low":
            priority = "Medium"
            reasons.append("Perda recente (≤3 meses)")

    name = lead.get("name") or "Oi"
    first = name.split()[0] if name else "Oi"
    company = lead.get("company") or "vocês"
    product = ""
    if playbook:
        product = str(playbook.get("product_summary") or playbook.get("company_name") or "")[:60]

    if priority == "High":
        opener = (
            f"{first}, voltei porque na última conversa o timing/orçamento era o bloqueio. "
            f"Mudou algo do lado de {company} que valha a gente retomar em 2 minutos?"
        )
    elif priority == "Medium":
        opener = (
            f"{first}, tudo bem? Ficamos de conversar sobre "
            f"{product or 'uma solução pro time'} e a thread esfriou. "
            f"Ainda faz sentido ou arquivamos?"
        )
    else:
        opener = (
            f"{first}, passando rápido: se a prioridade em {company} mudou, "
            f"me avisa que eu te mando um material objetivo — sem enrolação."
        )

    return {
        "priority": priority,
        "months_since_activity": months,
        "reasons": reasons,
        "suggested_opener": opener,
        "stage": stage,
        "lost_reason": lost_reason or None,
    }


def format_revival_for_prompt(lead: dict, playbook: dict | None = None) -> str:
    info = score_revival(lead, playbook)
    if (lead.get("stage") or "").lower() not in ("lost", "followup", "sdr"):
        # ainda útil em followup job
        pass
    lines = [
        "## Revival (skill closed-lost)",
        f"Prioridade: {info['priority']}",
        f"Opener sugerido: {info['suggested_opener']}",
    ]
    for r in info["reasons"]:
        lines.append(f"- {r}")
    lines.append("Mensagem curta, sem culpa, 1 CTA. Se não houver resposta em 2 toques, pare.")
    return "\n".join(lines)
