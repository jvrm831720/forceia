"""
ForceIA — Política de turnos por estágio (P1).

Define objetivo do turno, limites (perguntas, follow-ups) e pós-checks
na resposta visível antes de enviar ao lead.
"""

from __future__ import annotations

import re
from typing import Any

# max perguntas abertas na mesma resposta do agente
MAX_OPEN_QUESTIONS = {
    "sdr": 1,
    "qualified": 1,
    "closer": 1,
    "followup": 1,
    "won": 0,
    "lost": 1,
}

STAGE_OBJECTIVES: dict[str, str] = {
    "sdr": (
        "Objetivo deste turno: descobrir 1 peça que falta no BANT "
        "(need → authority → budget → timeline). Uma pergunta aberta por vez. "
        "Não empurre preço nem proposta ainda."
    ),
    "qualified": (
        "Objetivo deste turno: confirmar fit e avançar para agenda/closer. "
        "CTA claro de reunião ou próxima etapa. Sem redescobrir BANT completo."
    ),
    "closer": (
        "Objetivo deste turno: tratar 1 objeção (se houver) ou fechar próximo passo "
        "(proposta, pagamento, contrato). Não repita o pitch inteiro."
    ),
    "followup": (
        "Objetivo deste turno: reativar com valor novo + soft CTA. "
        "Não repita a última mensagem. Se já houve 3 follow-ups sem resposta, sugira handoff."
    ),
    "won": (
        "Objetivo: reforçar próximos passos pós-fechamento. Tom breve e positivo."
    ),
    "lost": (
        "Objetivo: revival suave ou respeitar o não. Uma pergunta de reabertura no máximo."
    ),
}

INTENT_GUIDANCE: dict[str, str] = {
    "ready_to_buy": (
        "Intent = pronto para comprar: priorize CTA de agenda, proposta ou link. "
        "Não faça discovery longo."
    ),
    "evaluating": (
        "Intent = avaliando: compare com cases/ROI do playbook; ofereça prova social ou demo."
    ),
    "researching": (
        "Intent = só pesquisando: modo educativo, sem pressão de fechamento."
    ),
    "objection": (
        "Intent = objeção: valide a preocupação, use resposta aprovada do playbook, "
        "não force fechamento neste turno."
    ),
    "nurture": (
        "Intent = nurture: soft touch, valor incremental, sem bombardear."
    ),
}

_QUESTION_RE = re.compile(r"\?")
_MULTI_PARA_RE = re.compile(r"\n{3,}")


def missing_bant_fields(bant: dict | None) -> list[str]:
    bant = bant or {}
    order = ("need", "authority", "budget", "timeline")
    missing = []
    for k in order:
        val = bant.get(k)
        if not val:
            missing.append(k)
            continue
        s = str(val).strip().lower()
        if s in ("nao", "não", "no", "n/a", "desconhecido", "unknown", "?", "-"):
            missing.append(k)
    return missing


def known_bant_summary(bant: dict | None) -> list[str]:
    bant = bant or {}
    lines = []
    for k in ("need", "authority", "budget", "timeline"):
        val = bant.get(k)
        if not val:
            continue
        s = str(val).strip()
        if s.lower() in ("nao", "não", "no", "n/a", "desconhecido", "unknown", "?", "-"):
            continue
        lines.append(f"{k}={s}")
    return lines


def format_turn_policy_for_prompt(
    *,
    stage: str,
    agent: str,
    lead: dict | None = None,
    intent: str | None = None,
    message_count: int = 0,
) -> str:
    stage = (stage or "sdr").lower()
    agent = (agent or "sdr").lower()
    lead = lead or {}
    bant = lead.get("bant") or {}
    meta = lead.get("metadata") or {}

    lines = ["## Política deste turno (obrigatório)"]
    obj = STAGE_OBJECTIVES.get(stage) or STAGE_OBJECTIVES["sdr"]
    lines.append(obj)

    max_q = MAX_OPEN_QUESTIONS.get(stage, 1)
    lines.append(f"Limite: no máximo {max_q} pergunta(s) com '?' nesta resposta.")
    lines.append("Mensagem curta estilo WhatsApp (ideal ≤ 3 frases curtas).")

    known = known_bant_summary(bant)
    missing = missing_bant_fields(bant)
    if known:
        lines.append(
            "Já sabemos (NÃO pergunte de novo): " + "; ".join(known) + "."
        )
    if missing and stage in ("sdr", "qualified"):
        lines.append(
            "Ainda falta no BANT (pergunte só o próximo): " + ", ".join(missing) + "."
        )

    objections = meta.get("objections") or []
    if isinstance(objections, str):
        objections = [objections]
    if objections:
        lines.append(
            "Objeções já levantadas (use resposta do playbook; não reabra do zero): "
            + "; ".join(str(o) for o in objections[-3:])
        )

    intent_key = (intent or meta.get("buying_intent") or "").lower()
    if intent_key in INTENT_GUIDANCE:
        lines.append(INTENT_GUIDANCE[intent_key])

    if stage == "followup":
        fu = int(meta.get("followup_count") or 0)
        lines.append(f"Follow-ups já enviados neste ciclo: {fu}.")
        if fu >= 3:
            lines.append("≥3 follow-ups sem tração → considere handoff=true no META.")

    if message_count <= 2 and stage == "sdr":
        lines.append("Início de conversa: cumprimente pelo nome se souber; uma pergunta só.")

    return "\n".join(lines)


def count_open_questions(text: str) -> int:
    if not text:
        return 0
    # ignora ? dentro de URLs grosseiramente
    cleaned = re.sub(r"https?://\S+", "", text)
    return len(_QUESTION_RE.findall(cleaned))


def trim_whatsapp_reply(text: str, *, max_chars: int = 900) -> str:
    t = (text or "").strip()
    t = _MULTI_PARA_RE.sub("\n\n", t)
    if len(t) <= max_chars:
        return t
    # corta no último parágrafo que caiba
    parts = t.split("\n\n")
    out: list[str] = []
    total = 0
    for p in parts:
        if total + len(p) + 2 > max_chars:
            break
        out.append(p)
        total += len(p) + 2
    if out:
        return "\n\n".join(out).strip()
    return t[: max_chars - 1].rstrip() + "…"


def enforce_turn_policy(
    reply: str,
    *,
    stage: str,
    agent: str = "sdr",
) -> dict[str, Any]:
    """Pós-check: limita '?' extras e tamanho WhatsApp."""
    stage = (stage or "sdr").lower()
    max_q = MAX_OPEN_QUESTIONS.get(stage, 1)
    original = reply or ""
    text = original
    issues: list[str] = []

    n_q = count_open_questions(text)
    if n_q > max_q > 0:
        # Mantém só até a max_q-ésima interrogação; o resto vira afirmação suave
        parts = re.split(r"(?<=[?])\s+", text)
        kept: list[str] = []
        q_seen = 0
        for part in parts:
            qs = count_open_questions(part)
            if q_seen + qs <= max_q:
                kept.append(part)
                q_seen += qs
            else:
                # remove '?' restantes neste pedaço
                cleaned = part.replace("?", ".")
                if cleaned.strip():
                    kept.append(cleaned.strip())
                issues.append("excess_questions")
        text = " ".join(kept).strip()
        n_q = count_open_questions(text)

    trimmed = trim_whatsapp_reply(text)
    if trimmed != text:
        issues.append("trimmed_length")
        text = trimmed

    return {
        "reply": text,
        "modified": text != original,
        "issues": issues,
        "open_questions": n_q,
        "max_open_questions": max_q,
    }


def should_handoff_on_objections(lead: dict | None, meta: dict | None = None) -> bool:
    """2+ objeções registradas neste lead → sugerir handoff."""
    lead = lead or {}
    meta_lead = dict(lead.get("metadata") or {})
    objections = meta_lead.get("objections") or []
    if isinstance(objections, str):
        objections = [objections]
    count = len([o for o in objections if o])
    if meta and meta.get("objection"):
        obj = str(meta["objection"])
        if obj and obj not in objections:
            count += 1
    return count >= 2
