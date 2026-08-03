"""
ForceIA - Ciclo de auto-melhoria assistida.

1. Amostra conversas won / lost
2. LLM analisa padroes e sugere novos prompts
3. Grava prompt_suggestions (status=pending)
4. Humano aprova → apply grava override ativo

Nada vai para producao sem aprovacao.
"""

from __future__ import annotations

import json
import re
from typing import Any

from prompts import load_prompt_from_file

AGENTS = ("sdr", "closer", "followup")

ANALYST_SYSTEM = """Voce e um coach de vendas B2B (WhatsApp, Brasil) e engenheiro de prompts.
Analise conversas reais de um time de agentes de IA (SDR, Closer, Follow-up).

Regras:
- Baseie-se APENAS nas conversas fornecidas (nao invente metricas).
- Seja especifico: cite padroes de mensagens que funcionaram ou falharam.
- Sugira prompts COMPLETOS em portugues (markdown), prontos para substituir o playbook.
- Nao remova o protocolo ---META---; os agentes dependem dele.
- Inclua no prompt sugerido a instrucao de terminar com ---META--- JSON.
- Responda SOMENTE com JSON valido no formato pedido.
"""


def _transcript(messages: list[dict], max_chars: int = 2500) -> str:
    lines = []
    for m in messages:
        role = m.get("role") or "?"
        agent = m.get("agent") or ""
        prefix = f"{role}" + (f"/{agent}" if agent else "")
        content = (m.get("content") or "").strip()
        if not content:
            continue
        lines.append(f"{prefix}: {content}")
    text = "\n".join(lines)
    if len(text) > max_chars:
        return text[: max_chars - 20] + "\n...[cortado]"
    return text


def sample_outcomes(
    *,
    list_leads_by_stage,
    get_messages_for_lead,
    workspace_id: str,
    per_outcome: int = 8,
) -> tuple[list[dict], list[dict]]:
    """Retorna (won_cases, lost_cases) com transcript."""
    won_cases: list[dict] = []
    lost_cases: list[dict] = []
    for stage, bucket in (("won", won_cases), ("lost", lost_cases)):
        leads = list_leads_by_stage(workspace_id, stage, limit=per_outcome)
        for lead in leads:
            msgs = get_messages_for_lead(lead["id"], limit=40)
            if len(msgs) < 2:
                continue
            bucket.append(
                {
                    "lead_id": lead["id"],
                    "name": lead.get("name"),
                    "company": lead.get("company"),
                    "bant": lead.get("bant") or {},
                    "transcript": _transcript(msgs),
                }
            )
    return won_cases, lost_cases


def build_analyst_user_payload(
    won: list[dict],
    lost: list[dict],
    current_prompts: dict[str, str],
) -> str:
    payload = {
        "won_count": len(won),
        "lost_count": len(lost),
        "won_samples": won[:10],
        "lost_samples": lost[:10],
        "current_prompts": current_prompts,
        "output_schema": {
            "summary": "string — resumo executivo em PT-BR",
            "insights": [
                {
                    "type": "win_pattern|loss_pattern|objection|timing|tone",
                    "detail": "string",
                    "evidence": "string curta",
                }
            ],
            "suggestions": [
                {
                    "agent": "sdr|closer|followup",
                    "title": "string curta",
                    "rationale": "por que mudar",
                    "diff_summary": "o que muda em bullets",
                    "suggested_prompt": "prompt markdown completo",
                }
            ],
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def parse_analyst_json(raw: str) -> dict[str, Any]:
    text = (raw or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(0))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
    return {"summary": "Falha ao parsear analise", "insights": [], "suggestions": []}


def run_analyst(
    client: Any,
    *,
    model: str,
    won: list[dict],
    lost: list[dict],
    current_prompts: dict[str, str],
) -> dict[str, Any]:
    user = build_analyst_user_payload(won, lost, current_prompts)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": ANALYST_SYSTEM},
            {
                "role": "user",
                "content": (
                    "Analise as amostras e proponha melhorias de prompt.\n"
                    "Garanta suggested_prompt completo para cada agent que valha a pena mudar "
                    "(pode omitir agent se nao houver mudanca clara).\n\n"
                    f"{user}"
                ),
            },
        ],
        temperature=0.35,
        max_tokens=4000,
    )
    raw = response.choices[0].message.content or ""
    return parse_analyst_json(raw)


def ensure_meta_protocol(prompt: str) -> str:
    """Garante que o prompt sugerido mencione o protocolo META."""
    if "---META---" in prompt:
        return prompt
    suffix = """

## Protocolo interno (obrigatorio)
Ao final de cada resposta, apos a mensagem ao lead, escreva:

---META---
{\"stage\":\"sdr|qualified|closer|won|lost|followup\",\"bant\":{\"need\":\"\",\"authority\":\"\",\"budget\":\"\",\"timeline\":\"\",\"score\":0},\"name\":null,\"company\":null,\"email\":null,\"intent\":\"\",\"objection\":null,\"handoff\":false,\"notes\":\"\"}
"""
    return prompt.rstrip() + suffix


def collect_current_prompts() -> dict[str, str]:
    return {agent: load_prompt_from_file(agent) for agent in AGENTS}
