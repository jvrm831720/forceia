"""
ForceIA — Playbook por workspace.

Estrutura canônica usada para personalizar SDR / Closer / Follow-up
com ICP, persona, pricing, cases, objeções, tom e FAQ do cliente.
"""

from __future__ import annotations

from typing import Any

PLAYBOOK_VERSION = 1

EMPTY_PLAYBOOK: dict[str, Any] = {
    "version": PLAYBOOK_VERSION,
    "company_name": "",
    "product_summary": "",
    "value_proposition": "",
    "icp": {
        "industries": [],
        "company_sizes": "",
        "roles": [],
        "geographies": "",
        "disqualifiers": [],
    },
    "persona": {
        "buyer_titles": [],
        "pains": [],
        "goals": [],
    },
    "pricing": {
        "model": "",
        "range": "",
        "notes": "",
    },
    "cases": [],  # [{title, result, segment}]
    "objections": [],  # [{objection, response}]
    "tone": {
        "style": "consultivo",
        "formality": "semi-formal",
        "do": [],
        "dont": [],
    },
    "faq": [],  # [{q, a}]
    "script_notes": "",
    "extra": "",
}

_WEIGHTS = {
    "company_name": 8,
    "product_summary": 12,
    "value_proposition": 12,
    "icp": 18,
    "persona": 12,
    "pricing": 12,
    "cases": 10,
    "objections": 10,
    "tone": 4,
    "faq": 2,
}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        parts = [p.strip() for p in value.replace(";", ",").split(",")]
        return [p for p in parts if p]
    return [str(value).strip()] if str(value).strip() else []


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _normalize_cases(raw: Any) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(raw, list):
        return out
    for item in raw[:12]:
        if not isinstance(item, dict):
            continue
        title = _as_str(item.get("title") or item.get("name"))
        result = _as_str(item.get("result") or item.get("outcome"))
        segment = _as_str(item.get("segment") or item.get("vertical"))
        if title or result:
            out.append({"title": title, "result": result, "segment": segment})
    return out


def _normalize_objections(raw: Any) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(raw, list):
        return out
    for item in raw[:20]:
        if not isinstance(item, dict):
            continue
        obj = _as_str(item.get("objection") or item.get("q") or item.get("objection_text"))
        resp = _as_str(item.get("response") or item.get("a") or item.get("answer"))
        if obj or resp:
            out.append({"objection": obj, "response": resp})
    return out


def _normalize_faq(raw: Any) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not isinstance(raw, list):
        return out
    for item in raw[:30]:
        if not isinstance(item, dict):
            continue
        q = _as_str(item.get("q") or item.get("question"))
        a = _as_str(item.get("a") or item.get("answer"))
        if q or a:
            out.append({"q": q, "a": a})
    return out


def normalize_playbook(raw: dict | None) -> dict[str, Any]:
    """Normaliza qualquer dict parcial para o schema canônico."""
    src = dict(raw or {})
    icp_src = src.get("icp") if isinstance(src.get("icp"), dict) else {}
    persona_src = src.get("persona") if isinstance(src.get("persona"), dict) else {}
    pricing_src = src.get("pricing") if isinstance(src.get("pricing"), dict) else {}
    tone_src = src.get("tone") if isinstance(src.get("tone"), dict) else {}

    return {
        "version": int(src.get("version") or PLAYBOOK_VERSION),
        "company_name": _as_str(src.get("company_name") or src.get("brand")),
        "product_summary": _as_str(src.get("product_summary") or src.get("product")),
        "value_proposition": _as_str(src.get("value_proposition") or src.get("value_prop")),
        "icp": {
            "industries": _as_list(icp_src.get("industries")),
            "company_sizes": _as_str(icp_src.get("company_sizes") or icp_src.get("size")),
            "roles": _as_list(icp_src.get("roles") or icp_src.get("buyer_roles")),
            "geographies": _as_str(icp_src.get("geographies") or icp_src.get("geo")),
            "disqualifiers": _as_list(icp_src.get("disqualifiers") or icp_src.get("anti_icp")),
        },
        "persona": {
            "buyer_titles": _as_list(persona_src.get("buyer_titles") or persona_src.get("titles")),
            "pains": _as_list(persona_src.get("pains")),
            "goals": _as_list(persona_src.get("goals")),
        },
        "pricing": {
            "model": _as_str(pricing_src.get("model")),
            "range": _as_str(pricing_src.get("range") or pricing_src.get("price_range")),
            "notes": _as_str(pricing_src.get("notes")),
        },
        "cases": _normalize_cases(src.get("cases")),
        "objections": _normalize_objections(src.get("objections")),
        "tone": {
            "style": _as_str(tone_src.get("style"), "consultivo") or "consultivo",
            "formality": _as_str(tone_src.get("formality"), "semi-formal") or "semi-formal",
            "do": _as_list(tone_src.get("do")),
            "dont": _as_list(tone_src.get("dont") or tone_src.get("donts")),
        },
        "faq": _normalize_faq(src.get("faq")),
        "script_notes": _as_str(src.get("script_notes") or src.get("script")),
        "extra": _as_str(src.get("extra") or src.get("notes")),
    }


def is_playbook_empty(pb: dict | None) -> bool:
    if not pb:
        return True
    n = normalize_playbook(pb)
    if n["company_name"] or n["product_summary"] or n["value_proposition"]:
        return False
    if any(n["icp"].values()) or any(n["persona"].values()):
        return False
    if any(n["pricing"].values()) or n["cases"] or n["objections"]:
        return False
    if n["faq"] or n["script_notes"] or n["extra"]:
        return False
    tone = n["tone"]
    if tone["do"] or tone["dont"]:
        return False
    if tone["style"] not in ("", "consultivo") or tone["formality"] not in ("", "semi-formal"):
        return False
    return True


def playbook_completeness(pb: dict | None) -> dict[str, Any]:
    """Score 0-100 + checklist por seção (para UI e onboarding)."""
    n = normalize_playbook(pb)
    checks: dict[str, bool] = {}
    score = 0

    checks["company_name"] = bool(n["company_name"])
    checks["product_summary"] = len(n["product_summary"]) >= 20
    checks["value_proposition"] = len(n["value_proposition"]) >= 15
    checks["icp"] = bool(
        n["icp"]["industries"] or n["icp"]["roles"] or n["icp"]["company_sizes"]
    )
    checks["persona"] = bool(n["persona"]["pains"] or n["persona"]["buyer_titles"])
    checks["pricing"] = bool(n["pricing"]["range"] or n["pricing"]["model"])
    checks["cases"] = len(n["cases"]) >= 1
    checks["objections"] = len(n["objections"]) >= 1
    checks["tone"] = bool(n["tone"]["do"] or n["tone"]["dont"] or n["tone"]["style"] != "consultivo")
    checks["faq"] = len(n["faq"]) >= 1

    for key, weight in _WEIGHTS.items():
        if checks.get(key):
            score += weight

    return {
        "score": min(100, score),
        "checks": checks,
        "ready": score >= 50,
        "sections_filled": sum(1 for v in checks.values() if v),
        "sections_total": len(checks),
    }


def extract_playbook_from_workspace(row: dict | None) -> dict[str, Any]:
    """Lê playbook da coluna dedicada ou de metadata.playbook (compat)."""
    if not row:
        return normalize_playbook({})
    raw = row.get("playbook")
    if not isinstance(raw, dict) or not raw:
        meta = row.get("metadata") or {}
        if isinstance(meta, dict):
            raw = meta.get("playbook")
    return normalize_playbook(raw if isinstance(raw, dict) else {})


def format_playbook_for_prompt(pb: dict | None, *, max_chars: int = 3500) -> str:
    """
    Renderiza o playbook em texto denso para o system prompt.
    Retorna string vazia se vazio — evita poluir o contexto.
    """
    n = normalize_playbook(pb)
    if is_playbook_empty(n):
        return ""

    lines: list[str] = ["## Playbook do cliente (fonte da verdade — priorize sobre conhecimento genérico)"]

    brand = n["company_name"] or "este cliente"
    lines.append(f"Você vende **em nome de {brand}**.")

    if n["product_summary"]:
        lines.append(f"Produto/serviço: {n['product_summary']}")
    if n["value_proposition"]:
        lines.append(f"Proposta de valor: {n['value_proposition']}")

    icp = n["icp"]
    icp_bits: list[str] = []
    if icp["industries"]:
        icp_bits.append("setores: " + ", ".join(icp["industries"]))
    if icp["company_sizes"]:
        icp_bits.append(f"porte: {icp['company_sizes']}")
    if icp["roles"]:
        icp_bits.append("cargos-alvo: " + ", ".join(icp["roles"]))
    if icp["geographies"]:
        icp_bits.append(f"geo: {icp['geographies']}")
    if icp_bits:
        lines.append("ICP: " + "; ".join(icp_bits) + ".")
    if icp["disqualifiers"]:
        lines.append(
            "Fora do ICP (desqualifique com honestidade): "
            + "; ".join(icp["disqualifiers"])
            + "."
        )

    persona = n["persona"]
    if persona["buyer_titles"]:
        lines.append("Títulos do comprador: " + ", ".join(persona["buyer_titles"]) + ".")
    if persona["pains"]:
        lines.append("Dores típicas: " + "; ".join(persona["pains"]) + ".")
    if persona["goals"]:
        lines.append("Objetivos do comprador: " + "; ".join(persona["goals"]) + ".")

    pricing = n["pricing"]
    if pricing["model"] or pricing["range"] or pricing["notes"]:
        pbits = [x for x in (pricing["model"], pricing["range"], pricing["notes"]) if x]
        lines.append("Pricing (não invente fora disso): " + " | ".join(pbits) + ".")

    if n["cases"]:
        lines.append("Cases / prova social:")
        for c in n["cases"][:5]:
            seg = f" ({c['segment']})" if c.get("segment") else ""
            result = f" → {c['result']}" if c.get("result") else ""
            lines.append(f"  - {c.get('title') or 'Case'}{seg}{result}")

    if n["objections"]:
        lines.append("Objeções e respostas aprovadas:")
        for o in n["objections"][:8]:
            lines.append(f"  - Se disser “{o.get('objection','')}”: {o.get('response','')}")

    tone = n["tone"]
    lines.append(
        f"Tom de voz: estilo {tone.get('style') or 'consultivo'}, "
        f"formalidade {tone.get('formality') or 'semi-formal'}."
    )
    if tone.get("do"):
        lines.append("Faça: " + "; ".join(tone["do"]) + ".")
    if tone.get("dont"):
        lines.append("Não faça: " + "; ".join(tone["dont"]) + ".")

    if n["faq"]:
        lines.append("FAQ interno (use se perguntarem):")
        for f in n["faq"][:6]:
            lines.append(f"  - P: {f.get('q','')} → R: {f.get('a','')}")

    if n["script_notes"]:
        lines.append(f"Notas de script / processo: {n['script_notes']}")
    if n["extra"]:
        lines.append(f"Contexto extra: {n['extra']}")

    lines.append(
        "Regras do playbook: não contradiga pricing/ICP/cases; se faltar info, diga que vai confirmar "
        "com o time em vez de inventar; desqualifique fora do ICP com respeito."
    )

    text = "\n".join(lines)
    if len(text) > max_chars:
        text = text[: max_chars - 20].rstrip() + "\n[…playbook truncado]"
    return text
