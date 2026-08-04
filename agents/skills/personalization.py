"""
Skill: Outreach Personalization Research.

Gera 3–5 ângulos de personalização e openers para o SDR (WhatsApp).
"""

from __future__ import annotations

from typing import Any


def build_personalization_brief(
    lead: dict,
    playbook: dict | None = None,
) -> dict[str, Any]:
    name = lead.get("name") or "por aí"
    company = lead.get("company") or "sua empresa"
    meta = lead.get("metadata") or {}
    enr = meta.get("enrichment") if isinstance(meta.get("enrichment"), dict) else {}
    title = enr.get("title") or ""
    product = ""
    pains: list[str] = []
    value = ""
    if playbook:
        product = str(playbook.get("product_summary") or playbook.get("company_name") or "")
        value = str(playbook.get("value_proposition") or "")
        persona = playbook.get("persona") if isinstance(playbook.get("persona"), dict) else {}
        pains = list(persona.get("pains") or [])[:3]

    angles: list[dict[str, str]] = []

    if title:
        angles.append(
            {
                "name": "Role-based",
                "category": "role",
                "data": f"Cargo: {title}",
                "opener": (
                    f"Vi que você atua como {title} na {company}. "
                    f"No dia a dia, o que mais consome tempo no comercial hoje?"
                ),
                "strength": "Strong",
            }
        )

    if company and company != "sua empresa":
        angles.append(
            {
                "name": "Company context",
                "category": "company",
                "data": f"Empresa: {company}",
                "opener": (
                    f"{name.split()[0] if name != 'por aí' else 'Oi'}, na {company} vocês já têm algum processo "
                    f"de follow-up no WhatsApp ou ainda é bem manual?"
                ),
                "strength": "Strong",
            }
        )

    if pains:
        pain = pains[0]
        angles.append(
            {
                "name": "ICP pain",
                "category": "pain",
                "data": pain,
                "opener": (
                    f"Muitos times no seu perfil citam “{pain}”. "
                    f"Isso ainda é realidade aí ou já resolveram de outro jeito?"
                ),
                "strength": "Medium",
            }
        )

    if value:
        angles.append(
            {
                "name": "Value prop hook",
                "category": "value",
                "data": value[:120],
                "opener": (
                    f"A gente ajuda times a {value[:80].rstrip('.')}. "
                    f"Faz sentido eu te mostrar em 2 min se encaixa na {company}?"
                ),
                "strength": "Medium",
            }
        )

    if not angles:
        angles.append(
            {
                "name": "Discovery soft",
                "category": "discovery",
                "data": "Sem enrichment rico",
                "opener": (
                    "Oi! Vi seu interesse e queria entender melhor o contexto de vocês "
                    "antes de te empurrar qualquer pitch. O que te trouxe aqui?"
                ),
                "strength": "Soft",
            }
        )

    best = next((a for a in angles if a["strength"] == "Strong"), angles[0])
    return {
        "prospect_summary": f"{name} · {title or 'cargo n/d'} @ {company}",
        "angles": angles[:5],
        "recommended": best,
        "product_hint": product[:200] if product else None,
    }


def format_personalization_for_prompt(lead: dict, playbook: dict | None = None) -> str:
    brief = build_personalization_brief(lead, playbook)
    lines = [
        "## Personalização de outreach (skill)",
        f"Prospect: {brief['prospect_summary']}",
        f"Melhor ângulo ({brief['recommended']['name']}): {brief['recommended']['opener']}",
        "Outros ângulos (use se o lead responder frio):",
    ]
    for a in brief["angles"][:3]:
        if a is brief["recommended"]:
            continue
        lines.append(f"- [{a['strength']}] {a['opener']}")
    lines.append("Não use opener genérico se houver ângulo Strong disponível.")
    return "\n".join(lines)
