"""
ForceIA - Camada de inteligencia dos agentes.

- Extrai BANT, nome, empresa, email e intencao a partir da conversa
- Monta contexto rico para o system prompt
- Parseia bloco ---META--- (JSON) retornado pelo LLM
- Calcula score de qualificacao
"""

from __future__ import annotations

import json
import re
from typing import Any

META_MARKER = "---META---"

_STAGE_TAGS = {
    "qualified": ("[QUALIFICADO]", "[QUALIFIED]"),
    "won": ("[FECHADO]", "[WON]"),
    "lost": ("[PERDIDO]", "[LOST]"),
    "followup": ("[FOLLOWUP]", "[FOLLOW-UP]"),
}

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_NAME_HINT_RE = re.compile(
    r"(?:meu nome e|me chamo|sou o|sou a|aqui e)\s+([A-Za-zÀ-ÿ]{2,}(?:\s+[A-Za-zÀ-ÿ]{2,}){0,2})",
    re.IGNORECASE,
)
_COMPANY_HINT_RE = re.compile(
    r"(?:trabalho na|da empresa|na empresa|represento a|somos a)\s+([A-Za-z0-9À-ÿ&.,\-]{2,}(?:\s+[A-Za-z0-9À-ÿ&.,\-]{2,}){0,4})",
    re.IGNORECASE,
)


def split_reply_and_meta(raw: str) -> tuple[str, dict[str, Any]]:
    if not raw:
        return "", {}
    if META_MARKER not in raw:
        return raw.strip(), {}
    visible, _, tail = raw.partition(META_MARKER)
    meta: dict[str, Any] = {}
    tail = tail.strip()
    tail = re.sub(r"^```(?:json)?\s*", "", tail)
    tail = re.sub(r"\s*```$", "", tail)
    try:
        parsed = json.loads(tail)
        if isinstance(parsed, dict):
            meta = parsed
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", tail, re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(0))
                if isinstance(parsed, dict):
                    meta = parsed
            except json.JSONDecodeError:
                pass
    return visible.strip(), meta


def stage_from_meta_or_tags(raw_reply: str, meta: dict[str, Any], current: str, can_transition) -> str:
    stage_hint = (meta.get("stage") or meta.get("next_stage") or "").strip().lower()
    mapping = {
        "qualified": "qualified", "qualificado": "qualified", "closer": "closer",
        "won": "won", "fechado": "won", "lost": "lost", "perdido": "lost",
        "followup": "followup", "follow-up": "followup", "sdr": "sdr",
    }
    if stage_hint in mapping:
        target = mapping[stage_hint]
        if can_transition(current, target):
            return target
    upper = raw_reply.upper()
    for target, tags in _STAGE_TAGS.items():
        if any(t in upper for t in tags):
            if can_transition(current, target):
                return target
            if target == "qualified" and can_transition(current, "closer"):
                return "closer"
    return current


def merge_bant(existing: dict | None, incoming: dict | None) -> dict:
    base = dict(existing or {})
    if not incoming:
        return base
    for key in ("budget", "authority", "need", "timeline"):
        val = incoming.get(key)
        if val is None or val == "":
            continue
        old = base.get(key)
        if not old or (isinstance(val, str) and len(str(val)) > len(str(old))):
            base[key] = val
    if "score" in incoming and incoming["score"] is not None:
        try:
            base["score"] = int(incoming["score"])
        except (TypeError, ValueError):
            pass
    return base


def bant_score(bant: dict | None) -> int:
    if not bant:
        return 0
    weights = {"need": 30, "authority": 25, "budget": 25, "timeline": 20}
    score = 0
    for key, w in weights.items():
        val = bant.get(key)
        if not val:
            continue
        s = str(val).strip().lower()
        if s in ("nao", "não", "no", "n/a", "desconhecido", "unknown", "?"):
            score += w // 4
        else:
            score += w
    if "score" in bant:
        try:
            declared = max(0, min(100, int(bant["score"])))
            score = int(round((score + declared) / 2))
        except (TypeError, ValueError):
            pass
    return max(0, min(100, score))


def is_bant_qualified(bant: dict | None, min_score: int = 60) -> bool:
    if not bant:
        return False
    has_need = bool(bant.get("need"))
    has_auth_or_budget = bool(bant.get("authority") or bant.get("budget"))
    return has_need and has_auth_or_budget and bant_score(bant) >= min_score


def extract_contact_hints(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    if not text:
        return out
    email = _EMAIL_RE.search(text)
    if email:
        out["email"] = email.group(0)
    name = _NAME_HINT_RE.search(text)
    if name:
        out["name"] = name.group(1).strip().title()
    company = _COMPANY_HINT_RE.search(text)
    if company:
        out["company"] = company.group(1).strip()
    return out


def build_lead_context(lead: dict, workspace_name: str = "ForceIA") -> str:
    bant = lead.get("bant") or {}
    meta = lead.get("metadata") or {}
    lines = [
        f"Voce atende pelo time {workspace_name}.",
        f"Estagio atual do lead: {lead.get('stage') or 'sdr'}.",
    ]
    if lead.get("name"):
        lines.append(f"Nome do lead: {lead['name']}.")
    if lead.get("company"):
        lines.append(f"Empresa: {lead['company']}.")
    if lead.get("email"):
        lines.append(f"Email: {lead['email']}.")
    if bant:
        lines.append("BANT conhecido ate agora:")
        for k in ("need", "authority", "budget", "timeline"):
            if bant.get(k):
                lines.append(f"  - {k}: {bant[k]}")
        score = bant_score(bant)
        lines.append(f"  - score: {score}/100")
    notes = meta.get("notes") or meta.get("last_intent")
    if notes:
        lines.append(f"Notas internas: {notes}")
    objections = meta.get("objections")
    if objections:
        lines.append(f"Objecoes ja levantadas: {objections}")
    lines.append(
        "Use essas informacoes: nao pergunte de novo o que ja sabe. "
        "Avance a conversa com base no que falta no BANT."
    )
    return "\n".join(lines)


def apply_meta_to_lead_fields(lead: dict, meta: dict, user_text: str) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    hints = extract_contact_hints(user_text)
    if meta.get("name") or hints.get("name"):
        updates["name"] = meta.get("name") or hints.get("name") or lead.get("name")
    if meta.get("company") or hints.get("company"):
        updates["company"] = meta.get("company") or hints.get("company") or lead.get("company")
    if meta.get("email") or hints.get("email"):
        updates["email"] = meta.get("email") or hints.get("email") or lead.get("email")
    incoming_bant = meta.get("bant") if isinstance(meta.get("bant"), dict) else {}
    for k in ("budget", "authority", "need", "timeline"):
        if meta.get(k) and k not in incoming_bant:
            incoming_bant[k] = meta[k]
    merged = merge_bant(lead.get("bant"), incoming_bant)
    if meta.get("score") is not None:
        merged = merge_bant(merged, {"score": meta.get("score")})
    merged["score"] = bant_score(merged)
    updates["bant"] = merged
    meta_store = dict(lead.get("metadata") or {})
    if meta.get("intent"):
        meta_store["last_intent"] = meta["intent"]
    if meta.get("objection"):
        prev = meta_store.get("objections") or []
        if isinstance(prev, str):
            prev = [prev]
        obj = str(meta["objection"])
        if obj not in prev:
            prev = list(prev) + [obj]
        meta_store["objections"] = prev[-5:]
    if meta.get("notes"):
        meta_store["notes"] = meta["notes"]
    if meta.get("handoff"):
        meta_store["handoff_requested"] = True
    updates["metadata"] = meta_store
    return updates


def build_system_prompt(base_prompt: str, lead: dict, workspace_name: str) -> str:
    context = build_lead_context(lead, workspace_name=workspace_name)
    protocol = """
## Protocolo interno (obrigatorio)

Ao final de CADA resposta, depois da mensagem para o lead, escreva exatamente:

---META---
{"stage":"sdr|qualified|closer|won|lost|followup","bant":{"need":"","authority":"","budget":"","timeline":"","score":0},"name":null,"company":null,"email":null,"intent":"","objection":null,"handoff":false,"notes":""}

Regras do META:
- Preencha so o que descobriu nesta conversa (nao invente).
- stage: so mude quando fizer sentido (ex.: BANT suficiente → "qualified"; fechou → "won").
- score: 0-100 estimado de qualificacao.
- O lead NAO deve ver o bloco ---META--- (ele e removido automaticamente).
- Mensagem ao lead: curta, WhatsApp, portugues brasileiro.
""".strip()
    return f"{base_prompt.strip()}\n\n## Contexto deste lead\n{context}\n\n{protocol}"
