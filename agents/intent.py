"""
ForceIA — Detecção automática ready_to_buy vs researching.

Combina sinais lexicais (PT-BR WhatsApp) + META do LLM.
Classes:
  ready_to_buy | evaluating | researching | objection | nurture | unknown
"""

from __future__ import annotations

import re
from typing import Any

READY_PATTERNS = [
    r"\bquero\s+fechar\b",
    r"\bvamos\s+fechar\b",
    r"\bfechamos\b",
    r"\bpode\s+mandar\s+(o\s+)?(contrato|proposta|boleto|pix|link)\b",
    r"\bquero\s+(contratar|assinar|começar|comecar)\b",
    r"\bfecha\s+(pra|para)\s+(mim|nós|nos)\b",
    r"\blink\s+de\s+pagamento\b",
    r"\bpassa\s+o\s+pix\b",
    r"\bcomo\s+pago\b",
    r"\bagenda\s+(hoje|amanh[aã]|essa\s+semana)\b",
    r"\bsim[,.]?\s+vamos\s+(em\s+frente|seguir)\b",
    r"\bautorizo\b",
    r"\bmanda\s+a\s+proposta\b",
]

EVAL_PATTERNS = [
    r"\bcompara(ndo|r)?\b",
    r"\bavaliando\b",
    r"\bpreciso\s+(ver|mostrar)\s+(com|pro)\s+(s[oó]cio|time|diretor)\b",
    r"\blevar\s+(pro|para\s+o)\s+time\b",
    r"\bqual\s+o\s+pre[cç]o\b",
    r"\bquanto\s+custa\b",
    r"\bdiferen[cç]a\s+entre\s+os\s+planos\b",
    r"\bcase\s+de\s+sucesso\b",
    r"\broi\b",
]

RESEARCH_PATTERNS = [
    r"\bs[oó]\s+estou\s+pesquisando\b",
    r"\bs[oó]\s+olhando\b",
    r"\bcuriosidade\b",
    r"\bquero\s+entender\b",
    r"\bcomo\s+funciona\b",
    r"\bme\s+explica\b",
    r"\bt[oô]\s+vendo\s+op[cç][oõ]es\b",
    r"\bainda\s+n[aã]o\s+sei\b",
    r"\binforma[cç][oõ]es\b",
]

OBJECTION_PATTERNS = [
    r"\best[aá]\s+caro\b",
    r"\bmuito\s+caro\b",
    r"\bn[aã]o\s+tenho\s+budget\b",
    r"\bsem\s+or[cç]amento\b",
    r"\bj[aá]\s+temos\s+(fornecedor|solu[cç][aã]o|time)\b",
    r"\bn[aã]o\s+[eé]\s+prioridade\b",
    r"\bdepois\s+(eu\s+)?vejo\b",
    r"\bn[aã]o\s+tenho\s+interesse\b",
    r"\bcancela\b",
    r"\bpara\s+de\s+me\s+mandar\b",
]


def _count_hits(text: str, patterns: list[str]) -> int:
    if not text:
        return 0
    return sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))


def detect_buying_intent(
    user_text: str,
    *,
    history: list[dict] | None = None,
    meta: dict | None = None,
) -> dict[str, Any]:
    meta = meta or {}
    signals: list[str] = []

    meta_intent = str(meta.get("intent") or meta.get("buying_intent") or "").strip().lower()
    meta_map = {
        "ready_to_buy": "ready_to_buy",
        "ready": "ready_to_buy",
        "buying": "ready_to_buy",
        "fechar": "ready_to_buy",
        "purchase": "ready_to_buy",
        "evaluating": "evaluating",
        "considering": "evaluating",
        "researching": "researching",
        "research": "researching",
        "curious": "researching",
        "objection": "objection",
        "not_now": "objection",
        "nurture": "nurture",
        "followup": "nurture",
    }
    if meta_intent in meta_map:
        intent = meta_map[meta_intent]
        signals.append(f"meta:{meta_intent}")
        conf = 0.85
        if meta.get("intent_confidence") is not None:
            try:
                conf = float(meta["intent_confidence"])
            except (TypeError, ValueError):
                pass
        return {
            "intent": intent,
            "confidence": max(0.0, min(1.0, conf)),
            "signals": signals,
            "source": "meta",
        }

    blob = user_text or ""
    if history:
        recent_user = [
            str(m.get("content") or "")
            for m in history[-6:]
            if (m.get("role") or "").lower() in ("user", "human", "lead")
        ]
        blob = " \n ".join(recent_user + [user_text or ""])

    ready_n = _count_hits(blob, READY_PATTERNS)
    eval_n = _count_hits(blob, EVAL_PATTERNS)
    research_n = _count_hits(blob, RESEARCH_PATTERNS)
    obj_n = _count_hits(blob, OBJECTION_PATTERNS)

    scores = {
        "ready_to_buy": ready_n * 3,
        "evaluating": eval_n * 2,
        "researching": research_n * 2,
        "objection": obj_n * 3,
    }
    best = max(scores, key=scores.get)
    best_score = scores[best]

    if best_score <= 0:
        return {
            "intent": "unknown",
            "confidence": 0.2,
            "signals": [],
            "source": "lexical",
        }

    if best == "ready_to_buy" and ready_n:
        signals.append(f"ready_hits:{ready_n}")
    if best == "evaluating" and eval_n:
        signals.append(f"eval_hits:{eval_n}")
    if best == "researching" and research_n:
        signals.append(f"research_hits:{research_n}")
    if best == "objection" and obj_n:
        signals.append(f"objection_hits:{obj_n}")

    conf = min(0.9, 0.35 + 0.2 * best_score)

    if ready_n and obj_n and obj_n >= ready_n:
        best = "objection"
        signals.append("objection_overrides_ready")

    return {
        "intent": best,
        "confidence": round(conf, 2),
        "signals": signals,
        "source": "lexical",
        "raw_counts": {
            "ready": ready_n,
            "evaluating": eval_n,
            "researching": research_n,
            "objection": obj_n,
        },
    }


def intent_label_pt(intent: str) -> str:
    return {
        "ready_to_buy": "pronto para comprar",
        "evaluating": "avaliando / comparando",
        "researching": "só pesquisando",
        "objection": "objeção / resistência",
        "nurture": "nutrição / follow-up",
        "unknown": "indefinido",
    }.get(intent, intent)
