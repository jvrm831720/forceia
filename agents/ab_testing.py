"""
ForceIA — A/B automático de prompts com métrica de conversão.

- Cada lead novo recebe variante A ou B (hash estável do phone)
- Variante B usa override em metadata.ab_prompts[agent] ou agent_prompt_overrides com tag
- Conversão: stage qualified/closer/won conta como sucesso
- Relatório compara taxas A vs B
"""

from __future__ import annotations

import hashlib
import os
from typing import Any


def ab_enabled() -> bool:
    return (os.getenv("FORCEIA_AB_TESTING") or "1").strip().lower() not in (
        "0",
        "false",
        "off",
        "no",
    )


def assign_variant(phone: str | None, workspace_id: str | None = None) -> str:
    """A ou B — estável por lead (mesmo phone = mesma variante)."""
    seed = f"{workspace_id or ''}:{phone or 'unknown'}"
    h = hashlib.sha256(seed.encode()).hexdigest()
    return "B" if int(h[:8], 16) % 2 == 1 else "A"


def ensure_lead_variant(lead: dict, workspace_id: str | None = None) -> tuple[dict, str]:
    """Garante metadata.ab_variant; retorna (lead_patch_meta, variant)."""
    meta = dict(lead.get("metadata") or {})
    existing = (meta.get("ab_variant") or "").upper()
    if existing in ("A", "B"):
        return meta, existing
    if not ab_enabled():
        meta["ab_variant"] = "A"
        return meta, "A"
    v = assign_variant(lead.get("phone"), workspace_id)
    meta["ab_variant"] = v
    return meta, v


def resolve_prompt_for_variant(
    *,
    agent: str,
    variant: str,
    workspace_id: str | None,
    load_prompt_fn,
) -> tuple[str, str]:
    """
    Retorna (prompt_text, source).
    A = prompt padrão (arquivo / override normal).
    B = override com suffix _b se existir, senão padrão (experimento neutro).
    """
    base = load_prompt_fn(agent, workspace_id=workspace_id)
    if (variant or "A").upper() != "B":
        return base, "control_A"

    # Tenta override B dedicado no DB
    try:
        from db import get_prompt_override

        alt = get_prompt_override(f"{agent}_b", workspace_id=workspace_id)
        if alt and len(alt.strip()) > 40:
            return alt, "variant_B_override"
        # Também tenta metadata global do workspace
    except Exception:
        pass

    # Fallback: mesmo prompt (ainda registra variante para análise futura)
    return base, "variant_B_fallback_same"


def conversion_success(stage: str | None) -> bool:
    return (stage or "").lower() in ("qualified", "closer", "won")


def record_ab_exposure(
    *,
    workspace_id: str,
    lead_id: str | None,
    variant: str,
    agent: str,
    source: str,
) -> None:
    try:
        from db import log_event

        log_event(
            "ab_exposure",
            {"variant": variant, "agent": agent, "source": source},
            lead_id=lead_id,
            workspace_id=workspace_id,
        )
    except Exception:
        pass


def compute_ab_report(leads: list[dict]) -> dict[str, Any]:
    """Taxa de conversão A vs B a partir dos leads."""
    buckets = {
        "A": {"total": 0, "converted": 0, "won": 0},
        "B": {"total": 0, "converted": 0, "won": 0},
    }
    for lead in leads:
        meta = lead.get("metadata") or {}
        v = (meta.get("ab_variant") or "").upper()
        if v not in buckets:
            continue
        buckets[v]["total"] += 1
        stage = (lead.get("stage") or "").lower()
        if conversion_success(stage):
            buckets[v]["converted"] += 1
        if stage == "won":
            buckets[v]["won"] += 1

    def rate(part: int, total: int) -> float:
        return round(part / total, 4) if total else 0.0

    report = {}
    for v, b in buckets.items():
        report[v] = {
            **b,
            "conversion_rate": rate(b["converted"], b["total"]),
            "win_rate": rate(b["won"], b["total"]),
        }

    a_c = report["A"]["conversion_rate"]
    b_c = report["B"]["conversion_rate"]
    lift = round(b_c - a_c, 4)
    winner = "B" if b_c > a_c + 0.02 and report["B"]["total"] >= 5 else (
        "A" if a_c > b_c + 0.02 and report["A"]["total"] >= 5 else "inconclusive"
    )

    return {
        "enabled": ab_enabled(),
        "variants": report,
        "lift_B_minus_A": lift,
        "winner": winner,
        "metric": "converted = stage in qualified|closer|won",
    }
