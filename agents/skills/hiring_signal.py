"""
Skill: Hiring Signal Prospector (adaptado ForceIA).

Analisa vagas / sinais de contratação como intent de compra:
- força do sinal (Strong / Medium / Soft)
- dor inferida da JD
- conexão com o produto do playbook
- opener personalizado para o decision-maker

Fonte de dados:
- metadata.hiring_signal no lead, ou
- payload enviado via API (role, company, jd_snippet, ...)
"""

from __future__ import annotations

import re
from typing import Any

_STRONG_RE = re.compile(
    r"\b(first\s+hire|primeira\s+contrata[cç][aã]o|from\s+the\s+ground\s+up|"
    r"do\s+zero|building\s+out|montar\s+o\s+time|greenfield|"
    r"no\s+existing|sem\s+time|primeiro\s+sdr|primeira\s+vaga)\b",
    re.I,
)
_MEDIUM_RE = re.compile(
    r"\b(scaling|escalando|growing\s+team|expandindo|hiring\s+additional|"
    r"nova\s+vaga|open\s+position|estamos\s+contratando)\b",
    re.I,
)
_TOOLS_RE = re.compile(
    r"\b(salesforce|hubspot|pipedrive|outreach|salesloft|gong|apollo|"
    r"linkedin\s+sales\s+navigator|whatsapp|rd\s+station|"
    r"excel|google\s+sheets|planilha)\b",
    re.I,
)


def _product_bits(playbook: dict | None) -> tuple[str, str]:
    if not playbook:
        return "", ""
    product = str(playbook.get("product_summary") or playbook.get("company_name") or "")
    value = str(playbook.get("value_proposition") or "")
    return product, value


def _infer_pain(role: str, jd: str) -> str:
    text = f"{role} {jd}".lower()
    if any(x in text for x in ("sdr", "bdr", "outbound", "prospec")):
        if _STRONG_RE.search(text):
            return "Montando outbound do zero — sem playbook/ferramenta ainda"
        return "Expandindo time de prospecção — processo e stack sob pressão"
    if any(x in text for x in ("revops", "revenue operations", "ops comercial")):
        return "Formalizando RevOps — forecast e CRM ainda ad hoc"
    if any(x in text for x in ("closer", "account executive", "ae ", "executivo de contas")):
        return "Aumentando capacidade de fechamento — pipeline precisa de velocidade"
    if any(x in text for x in ("customer success", "cs manager", "sucesso do cliente")):
        return "Escala de CS — retenção e onboarding sob demanda"
    if jd.strip():
        return "Contratação indica prioridade de investimento na função"
    return "Sinal de contratação — validar dor na conversa"


def _signal_strength(role: str, jd: str) -> str:
    blob = f"{role}\n{jd}"
    if _STRONG_RE.search(blob):
        return "Strong"
    if _MEDIUM_RE.search(blob):
        return "Medium"
    if (role or jd).strip():
        return "Soft"
    return "Soft"


def _tools_mentioned(jd: str) -> list[str]:
    found = []
    for m in _TOOLS_RE.finditer(jd or ""):
        tok = m.group(0).strip()
        if tok.lower() not in {x.lower() for x in found}:
            found.append(tok)
    return found[:8]


def _product_connection(role: str, jd: str, playbook: dict | None) -> str:
    product, value = _product_bits(playbook)
    strength = _signal_strength(role, jd)
    base = product or "sua solução"
    if strength == "Strong":
        return (
            f"Primeira contratação / time do zero: decisões de stack agora definem velocidade. "
            f"{base} encaixa como base do processo"
            + (f" ({value[:80]})" if value else "")
        )
    if strength == "Medium":
        return (
            f"Time em expansão para “{role or 'a função'}”: precisa de processo repetível. "
            f"Conectar {base} à dor de escala."
        )
    return f"Sinal de contratação em {role or 'área relacionada'} — validar se {base} resolve a causa."


def _opener(
    *,
    dm_name: str | None,
    company: str | None,
    role: str,
    strength: str,
    playbook: dict | None,
) -> str:
    first = (dm_name or "Oi").split()[0]
    co = company or "a empresa"
    product, _ = _product_bits(playbook)
    role_l = role or "essa função"

    if strength == "Strong":
        return (
            f"{first}, vi que {co} está contratando {role_l} (parece first hire / do zero). "
            f"As escolhas de processo e ferramenta agora costumam definir o ritmo do time por anos"
            + (f" — a gente ajuda com {product[:60]}" if product else "")
            + ". Faz sentido uma conversa curta?"
        )
    if strength == "Medium":
        return (
            f"{first}, notei que {co} está ampliando o time ({role_l}). "
            f"Quando a fila de contratação sobe, o gargalo costuma ser processo, não só headcount. "
            f"Quer que eu te mostre como outros times destravaram isso?"
        )
    return (
        f"{first}, vi movimento de contratação em {co} ({role_l}). "
        f"Se a prioridade for acelerar resultado dessa área, posso te mandar um ângulo objetivo — sem pitch longo."
    )


def analyze_hiring_signal(
    *,
    role: str = "",
    company: str = "",
    domain: str = "",
    jd_snippet: str = "",
    posting_url: str = "",
    posting_date: str = "",
    decision_maker_name: str = "",
    decision_maker_title: str = "",
    playbook: dict | None = None,
) -> dict[str, Any]:
    strength = _signal_strength(role, jd_snippet)
    pain = _infer_pain(role, jd_snippet)
    connection = _product_connection(role, jd_snippet, playbook)
    tools = _tools_mentioned(jd_snippet)
    opener = _opener(
        dm_name=decision_maker_name or None,
        company=company or None,
        role=role,
        strength=strength,
        playbook=playbook,
    )

    return {
        "company": company or None,
        "domain": domain or None,
        "role": role or None,
        "posting_url": posting_url or None,
        "posting_date": posting_date or None,
        "jd_snippet": (jd_snippet or "")[:500] or None,
        "pain_point": pain,
        "product_connection": connection,
        "tools_mentioned": tools,
        "team_size_signal": (
            "first hire / greenfield"
            if strength == "Strong"
            else ("scaling team" if strength == "Medium" else "replacement / unclear")
        ),
        "signal_strength": strength,
        "decision_maker": {
            "name": decision_maker_name or None,
            "title": decision_maker_title or None,
        },
        "suggested_opener": opener,
        "priority": {"Strong": "HIGH", "Medium": "MEDIUM", "Soft": "LOW"}.get(strength, "LOW"),
    }


def hiring_signal_from_lead(lead: dict, playbook: dict | None = None) -> dict[str, Any] | None:
    """Lê metadata.hiring_signal e enriquece a análise."""
    meta = lead.get("metadata") or {}
    raw = meta.get("hiring_signal")
    if not isinstance(raw, dict) or not raw:
        return None
    return analyze_hiring_signal(
        role=str(raw.get("role") or raw.get("title") or ""),
        company=str(raw.get("company") or lead.get("company") or ""),
        domain=str(raw.get("domain") or ""),
        jd_snippet=str(raw.get("jd_snippet") or raw.get("description") or ""),
        posting_url=str(raw.get("posting_url") or raw.get("url") or ""),
        posting_date=str(raw.get("posting_date") or ""),
        decision_maker_name=str(raw.get("decision_maker_name") or lead.get("name") or ""),
        decision_maker_title=str(raw.get("decision_maker_title") or ""),
        playbook=playbook,
    )


def format_hiring_signal_for_prompt(lead: dict, playbook: dict | None = None) -> str:
    info = hiring_signal_from_lead(lead, playbook)
    if not info:
        return ""
    lines = [
        "## Hiring Signal (skill prospector)",
        f"Força: {info['signal_strength']} ({info['priority']}) · role: {info.get('role') or 'n/d'}",
        f"Dor inferida: {info['pain_point']}",
        f"Conexão com produto: {info['product_connection']}",
        f"Opener sugerido: {info['suggested_opener']}",
    ]
    if info.get("tools_mentioned"):
        lines.append("Tools na JD: " + ", ".join(info["tools_mentioned"]))
    lines.append("Use o sinal de contratação na abertura; não invente detalhes que não estão na JD.")
    return "\n".join(lines)
