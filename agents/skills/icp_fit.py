"""
Skill: Enrich & Score Lead (ICP Fit).

Pontua 1–100 alinhamento do lead ao ICP do playbook + seniority + dados.
"""

from __future__ import annotations

import re
from typing import Any

_SENIORITY_PATTERNS: list[tuple[re.Pattern[str], int, str]] = [
    (re.compile(r"\b(ceo|cto|cfo|cmo|coo|founder|fundador|s[oó]cio|owner|dono)\b", re.I), 28, "C-level/Founder"),
    (re.compile(r"\b(vp|vice[\s-]?presidente|head)\b", re.I), 24, "VP/Head"),
    (re.compile(r"\b(diretor|diretora|director)\b", re.I), 20, "Director"),
    (re.compile(r"\b(gerente|manager|coordenador)\b", re.I), 14, "Manager"),
    (re.compile(r"\b(analista|assistant|assistente|estagi[aá]rio|junior|j[uú]nior)\b", re.I), 6, "Junior/Entry"),
]


def _title_from_lead(lead: dict) -> str:
    meta = lead.get("metadata") or {}
    enr = meta.get("enrichment") if isinstance(meta.get("enrichment"), dict) else {}
    return str(enr.get("title") or meta.get("title") or "")


def _seniority_score(title: str) -> tuple[int, str]:
    t = title or ""
    for pat, pts, label in _SENIORITY_PATTERNS:
        if pat.search(t):
            return pts, label
    if t.strip():
        return 12, "Unknown title"
    return 5, "Sem cargo"


def _icp_match_score(lead: dict, playbook: dict | None) -> tuple[int, list[str]]:
    """Até 40 pts: indústria, roles, disqualifiers."""
    if not playbook:
        return 15, ["Playbook sem ICP — score baseline"]
    icp = playbook.get("icp") if isinstance(playbook.get("icp"), dict) else {}
    persona = playbook.get("persona") if isinstance(playbook.get("persona"), dict) else {}
    reasons: list[str] = []
    score = 0

    company = (lead.get("company") or "").lower()
    title = _title_from_lead(lead).lower()
    text_blob = f"{company} {title} {(lead.get('name') or '')}".lower()

    roles = [str(r).lower() for r in (icp.get("roles") or []) + (persona.get("buyer_titles") or [])]
    if roles:
        hit = any(r in title or r in text_blob for r in roles if len(r) > 2)
        if hit:
            score += 18
            reasons.append("Cargo alinhado ao ICP")
        else:
            score += 6
            reasons.append("Cargo não confirma ICP de roles")
    else:
        score += 10
        reasons.append("ICP roles não definidos")

    industries = [str(i).lower() for i in (icp.get("industries") or [])]
    if industries and company:
        # sem industry do lead: pontua parcial se company preenchida
        score += 12
        reasons.append("Empresa conhecida (indústria a validar na conversa)")
    elif industries:
        score += 4
        reasons.append("Indústria ICP definida; empresa ainda desconhecida")
    else:
        score += 8

    disq = [str(d).lower() for d in (icp.get("disqualifiers") or [])]
    for d in disq:
        if d and d in text_blob:
            score = max(0, score - 20)
            reasons.append(f"Possível disqualifier: {d}")
            break

    return min(40, score), reasons


def _data_completeness(lead: dict) -> tuple[int, list[str]]:
    pts = 0
    reasons = []
    meta = lead.get("metadata") or {}
    enr = meta.get("enrichment") if isinstance(meta.get("enrichment"), dict) else {}
    if lead.get("name") or enr.get("name"):
        pts += 4
    if lead.get("company") or enr.get("company"):
        pts += 4
    if lead.get("email") or enr.get("email"):
        pts += 4
        reasons.append("Email presente")
    if enr.get("linkedin_url") or enr.get("title"):
        pts += 3
        reasons.append("Enrichment parcial")
    return min(15, pts), reasons


def _engagement_signals(lead: dict) -> tuple[int, list[str]]:
    pts = 0
    reasons = []
    meta = lead.get("metadata") or {}
    intent = str(meta.get("buying_intent") or meta.get("last_intent") or "").lower()
    if intent in ("ready_to_buy", "ready", "comprar"):
        pts += 10
        reasons.append("Intent ready_to_buy")
    elif intent in ("evaluating", "avaliando"):
        pts += 7
        reasons.append("Intent evaluating")
    elif intent:
        pts += 3
    stage = (lead.get("stage") or "").lower()
    if stage in ("qualified", "closer"):
        pts += 5
    elif stage == "won":
        pts += 10
    return min(15, pts), reasons


def compute_icp_fit(lead: dict, playbook: dict | None = None) -> dict[str, Any]:
    sen_pts, sen_label = _seniority_score(_title_from_lead(lead))
    icp_pts, icp_reasons = _icp_match_score(lead, playbook)
    data_pts, data_reasons = _data_completeness(lead)
    eng_pts, eng_reasons = _engagement_signals(lead)

    total = min(100, sen_pts + icp_pts + data_pts + eng_pts)
    if total >= 80:
        grade, priority = "A", "HIGH — priorizar outreach personalizado"
    elif total >= 65:
        grade, priority = "B", "MEDIUM-HIGH — qualificar com BANT"
    elif total >= 45:
        grade, priority = "C", "MEDIUM — nutrir / validar fit"
    elif total >= 25:
        grade, priority = "D", "LOW — só se capacidade sobrar"
    else:
        grade, priority = "F", "DEPRIORITIZE — fora do ICP ou dados insuficientes"

    return {
        "score": total,
        "grade": grade,
        "priority": priority,
        "breakdown": {
            "seniority": {"points": sen_pts, "max": 30, "label": sen_label},
            "icp_match": {"points": icp_pts, "max": 40, "reasons": icp_reasons},
            "data_completeness": {"points": data_pts, "max": 15, "reasons": data_reasons},
            "engagement": {"points": eng_pts, "max": 15, "reasons": eng_reasons},
        },
    }


def format_icp_for_prompt(lead: dict, playbook: dict | None = None) -> str:
    info = compute_icp_fit(lead, playbook)
    lines = [
        "## ICP Fit Score (skill enrich-and-score)",
        f"Score: {info['score']}/100 (grade {info['grade']}) — {info['priority']}",
    ]
    bd = info["breakdown"]
    lines.append(
        f"Seniority: {bd['seniority']['points']}/30 ({bd['seniority']['label']}); "
        f"ICP: {bd['icp_match']['points']}/40; "
        f"Dados: {bd['data_completeness']['points']}/15; "
        f"Engajamento: {bd['engagement']['points']}/15"
    )
    if info["score"] < 40:
        lines.append("Ação: valide fit com honestidade; não force pitch se fora do ICP.")
    elif info["score"] >= 80:
        lines.append("Ação: trate como hot lead — personalize e avance rápido.")
    return "\n".join(lines)
