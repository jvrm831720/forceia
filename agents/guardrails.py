"""
ForceIA — Guardrails rígidos de confiabilidade.

Regras:
- Nunca inventar preço fora do playbook
- Nunca prometer prazo que não esteja no playbook/FAQ
- Se faltar info: admitir e oferecer confirmar com o time

Camadas:
1. Instrução no system prompt (prevenção)
2. Scan pós-resposta (detecção + sanitização leve)
"""

from __future__ import annotations

import re
from typing import Any

# Valores monetários / percentuais soltos
_PRICE_RE = re.compile(
    r"(?:"
    r"R\$\s*[\d.]+(?:,\d{2})?"
    r"|\b\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*(?:reais|real)\b"
    r"|\b\d+(?:,\d+)?\s*%\s*(?:de\s+desconto|off)?\b"
    r"|\b(?:custa|custo|preço|preco|investimento|mensalidade|anual)\s*(?:de\s+|é\s+|eh\s+|de\s+R\$\s*)?[\d.R$\s,]{3,}"
    r")",
    re.IGNORECASE,
)

# Prazos absolutos perigosos
_DEADLINE_RE = re.compile(
    r"(?:"
    r"\bem\s+\d+\s*(?:minutos?|horas?|dias?|semanas?|meses?)\b"
    r"|\b(?:ainda\s+hoje|ainda\s+hoje|até\s+amanhã|ate\s+amanha|ainda\s+essa\s+semana)\b"
    r"|\b(?:garantimos|garantia\s+de|prometemos|com\s+certeza\s+em)\s+[^.]{0,40}\b(?:dia|hora|semana)\b"
    r"|\bimplementa(?:ção|cao)?\s+em\s+\d+\b"
    r"|\bentrega(?:mos)?\s+em\s+\d+\b"
    r")",
    re.IGNORECASE,
)

_SAFE_FALLBACK_PRICE = (
    "Sobre valores, trabalho só com a tabela oficial do time — "
    "posso te passar a faixa aprovada ou confirmar o número exato com alguém daqui, pode ser?"
)

_SAFE_FALLBACK_DEADLINE = (
    "Sobre prazo, não quero te passar uma data que eu não possa cumprir. "
    "Vou confirmar com o time e te respondo com o prazo real, combinado?"
)


def _pricing_allowed_text(playbook: dict | None) -> str:
    if not playbook:
        return ""
    pricing = playbook.get("pricing") if isinstance(playbook.get("pricing"), dict) else {}
    parts = [
        str(pricing.get("model") or ""),
        str(pricing.get("range") or ""),
        str(pricing.get("notes") or ""),
    ]
    faq_bits = []
    for f in playbook.get("faq") or []:
        if isinstance(f, dict):
            faq_bits.append(f"{f.get('q', '')} {f.get('a', '')}")
    return " ".join(parts + faq_bits).lower()


def _deadline_allowed_text(playbook: dict | None) -> str:
    if not playbook:
        return ""
    chunks: list[str] = [
        str(playbook.get("script_notes") or ""),
        str(playbook.get("extra") or ""),
        str(playbook.get("product_summary") or ""),
    ]
    for f in playbook.get("faq") or []:
        if isinstance(f, dict):
            chunks.append(f"{f.get('q', '')} {f.get('a', '')}")
    return " ".join(chunks).lower()


def format_guardrails_for_prompt(playbook: dict | None = None) -> str:
    """Bloco obrigatório no system prompt."""
    pricing = _pricing_allowed_text(playbook)
    lines = [
        "## Guardrails de confiabilidade (OBRIGATÓRIO — nunca viole)",
        "1. **Preço:** NUNCA invente valor, desconto ou condição comercial que não esteja no Playbook.",
        "2. **Prazo:** NUNCA prometa data, SLA ou tempo de entrega/implementação que não esteja no Playbook/FAQ.",
        "3. Se o lead pedir preço/prazo e você NÃO tiver no playbook: diga que vai confirmar com o time — não chute.",
        "4. Não diga “garanto”, “com certeza em X dias”, “só hoje” sem base no playbook.",
        "5. Prefira honestidade a persuasão falsa: confiança > fechamento precipitado.",
    ]
    if pricing.strip():
        lines.append(
            f"6. Pricing permitido (único autorizado a citar): {_pricing_allowed_text(playbook)[:400]}"
        )
    else:
        lines.append(
            "6. Pricing no playbook está vazio — se perguntarem preço, diga que um humano do time confirma o valor."
        )
    return "\n".join(lines)


def _token_overlap(fragment: str, allowed: str) -> bool:
    """Heurística: se números do fragmento aparecem no texto autorizado."""
    if not fragment or not allowed:
        return False
    nums = re.findall(r"\d+[\d.,]*", fragment)
    if not nums:
        return fragment.lower() in allowed
    for n in nums:
        if n in allowed or n.replace(".", "") in allowed:
            return True
    return False


def scan_reply(
    reply: str,
    *,
    playbook: dict | None = None,
) -> dict[str, Any]:
    """Detecta possíveis violações de preço/prazo."""
    text = reply or ""
    issues: list[dict[str, str]] = []
    allowed_price = _pricing_allowed_text(playbook)
    allowed_deadline = _deadline_allowed_text(playbook)

    for m in _PRICE_RE.finditer(text):
        frag = m.group(0)
        if allowed_price and _token_overlap(frag, allowed_price):
            continue
        # Se há pricing no playbook e o fragmento é só menção genérica sem número inventado, ok parcial
        if not re.search(r"\d", frag) and allowed_price:
            continue
        if not allowed_price or not _token_overlap(frag, allowed_price):
            issues.append({"type": "price", "fragment": frag[:80]})

    for m in _DEADLINE_RE.finditer(text):
        frag = m.group(0)
        if allowed_deadline and _token_overlap(frag, allowed_deadline):
            continue
        issues.append({"type": "deadline", "fragment": frag[:80]})

    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "has_price_risk": any(i["type"] == "price" for i in issues),
        "has_deadline_risk": any(i["type"] == "deadline" for i in issues),
    }


def enforce_guardrails(
    reply: str,
    *,
    playbook: dict | None = None,
    strict: bool = True,
) -> dict[str, Any]:
    """
    Sanitiza a resposta se houver risco.

    strict=True: substitui trechos de risco por fallback honesto.
    """
    scan = scan_reply(reply, playbook=playbook)
    if scan["ok"] or not strict:
        return {"reply": reply, "modified": False, **scan}

    text = reply or ""
    modified = False

    if scan["has_price_risk"]:
        # Remove menções de preço suspeitas e anexa fallback
        text2 = _PRICE_RE.sub("[valor sob confirmação]", text)
        if text2 != text:
            text = text2
            modified = True
        if _SAFE_FALLBACK_PRICE not in text:
            text = (text.rstrip() + "\n\n" + _SAFE_FALLBACK_PRICE).strip()
            modified = True

    if scan["has_deadline_risk"]:
        text2 = _DEADLINE_RE.sub("no prazo que o time confirmar", text)
        if text2 != text:
            text = text2
            modified = True
        if _SAFE_FALLBACK_DEADLINE not in text:
            text = (text.rstrip() + "\n\n" + _SAFE_FALLBACK_DEADLINE).strip()
            modified = True

    return {
        "reply": text,
        "modified": modified,
        "ok": False,
        "issues": scan["issues"],
        "has_price_risk": scan["has_price_risk"],
        "has_deadline_risk": scan["has_deadline_risk"],
    }
