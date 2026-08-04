"""
Skill: Pre-Call Research Brief.

Síntese acionável para o Closer antes de avançar/agendar.
"""

from __future__ import annotations

from typing import Any

from intelligence import bant_score


def build_pre_call_brief(
    lead: dict,
    playbook: dict | None = None,
    *,
    messages: list[dict] | None = None,
) -> dict[str, Any]:
    name = lead.get("name") or "Lead"
    company = lead.get("company") or "—"
    stage = lead.get("stage") or "sdr"
    bant = lead.get("bant") or {}
    meta = lead.get("metadata") or {}
    enr = meta.get("enrichment") if isinstance(meta.get("enrichment"), dict) else {}
    intent = meta.get("buying_intent") or meta.get("last_intent") or "—"
    objections = meta.get("objections") or []
    if isinstance(objections, str):
        objections = [objections]

    product = ""
    cases: list[str] = []
    if playbook:
        product = str(playbook.get("product_summary") or "")[:200]
        for c in (playbook.get("cases") or [])[:2]:
            if isinstance(c, dict):
                cases.append(f"{c.get('title', '')}: {c.get('result', '')}".strip(": "))

    talking_points = []
    if bant.get("need"):
        talking_points.append(f"Dor declarada: {bant['need']}")
    if bant.get("timeline"):
        talking_points.append(f"Prazo: {bant['timeline']}")
    if bant.get("budget"):
        talking_points.append(f"Budget: {bant['budget']}")
    if cases:
        talking_points.append(f"Case útil: {cases[0]}")
    if not talking_points:
        talking_points.append("Ainda falta BANT — use a call para Need + Authority")

    questions = [
        "O que acontece se isso não for resolvido nos próximos 90 dias?",
        "Além de você, quem mais precisa validar a decisão?",
    ]
    if not bant.get("budget"):
        questions.append("Já existe faixa de investimento em mente ou depende de ROI?")

    landmines = []
    if objections:
        landmines.append(f"Objeções já levantadas: {'; '.join(str(o) for o in objections[-3:])}")
    landmines.append("Não invente preço/prazo fora do playbook (guardrails)")

    recent = []
    for m in (messages or [])[-4:]:
        role = m.get("role") or "?"
        content = (m.get("content") or "").strip()
        if "---META---" in content:
            content = content.split("---META---", 1)[0].strip()
        if content:
            recent.append({"role": role, "content": content[:200]})

    return {
        "executive_summary": (
            f"Call com {name} ({enr.get('title') or 'cargo n/d'}) @ {company}. "
            f"Stage {stage}, intent {intent}, BANT score {bant_score(bant)}/100."
        ),
        "person": {
            "name": name,
            "title": enr.get("title"),
            "company": company,
            "email": lead.get("email") or enr.get("email"),
            "linkedin": enr.get("linkedin_url"),
        },
        "bant": bant,
        "intent": intent,
        "talking_points": talking_points,
        "questions": questions,
        "landmines": landmines,
        "product_context": product or None,
        "recent_messages": recent,
        "cases": cases,
    }


def format_pre_call_for_prompt(
    lead: dict,
    playbook: dict | None = None,
    *,
    messages: list[dict] | None = None,
) -> str:
    b = build_pre_call_brief(lead, playbook, messages=messages)
    lines = [
        "## Pre-Call Brief (skill)",
        b["executive_summary"],
        "Talking points:",
    ]
    for tp in b["talking_points"]:
        lines.append(f"- {tp}")
    lines.append("Perguntas prioritárias:")
    for q in b["questions"][:3]:
        lines.append(f"- {q}")
    lines.append("Landmines:")
    for lm in b["landmines"]:
        lines.append(f"- {lm}")
    return "\n".join(lines)
