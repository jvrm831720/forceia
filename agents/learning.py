"""
ForceIA - Ciclo de auto-melhoria assistida (STaR + SPIN adaptados).

Inspirado em:
- STaR (Zelikman et al., NeurIPS 2022): bootstrapping por racionalizacao —
  quando o agente falha, gera o raciocinio/resposta que *teria* funcionado
  e usa so os casos filtrados como sinal de aprendizado.
- SPIN (Chen et al., ICML 2024): self-play — compara respostas "reais"
  (conversas won / boas) vs "generated" (lost / fracas do proprio agente)
  e aprende a preferir o padrao vencedor, sem labels humanos extras.

Fluxo ForceIA (prompts, nao fine-tune de pesos):
1. Amostra won / lost com transcripts
2. Monta pares preferencia (SPIN): real vs generated
3. Racionaliza lost (STaR): counterfactual "o que deveria ter dito"
4. Filtra racionalizacoes uteis
5. LLM coach gera sugestoes de prompt a partir de pares + racionalizacoes
6. Grava prompt_suggestions (pending) — humano aprova → override

Nada vai para producao sem aprovacao.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from prompts import load_prompt_from_file

AGENTS = ("sdr", "closer", "followup")

ANALYST_SYSTEM = """Voce e um coach de vendas B2B (WhatsApp, Brasil) e engenheiro de prompts.
Analise conversas reais de um time de agentes de IA (SDR, Closer, Follow-up).

Voce recebe:
1. Pares preferencia no estilo SPIN: "real" (ganhou / bom) vs "generated" (perdeu / fraco)
2. Racionalizacoes STaR: para conversas perdidas, a resposta ideal counterfactual
3. Prompts atuais dos agentes

Regras:
- Baseie-se APENAS nos dados fornecidos (nao invente metricas).
- Prefira padroes que distinguem won de lost (self-play discrimination).
- Use racionalizacoes como exemplos de "como deveria ter sido".
- Seja especifico: cite mensagens ou turnos que funcionaram ou falharam.
- Sugira prompts COMPLETOS em portugues (markdown), prontos para substituir o playbook.
- Nao remova o protocolo ---META---; os agentes dependem dele.
- Inclua no prompt sugerido a instrucao de terminar com ---META--- JSON.
- Responda SOMENTE com JSON valido no formato pedido.
"""

RATIONALIZER_SYSTEM = """Voce e um SDR/Closer senior de vendas B2B no WhatsApp (Brasil).
Recebe uma conversa que TERMINOU EM PERDA (lost).

Sua tarefa (STaR rationalization):
1. Identifique o ponto de ruptura (onde a conversa esfriou ou a objecao matou o deal).
2. Escreva a resposta ideal que o agente DEVERIA ter dado naquele turno critico.
3. Explique em 1-2 frases o principio (ex.: validar objecao antes de preco).

Responda SOMENTE com JSON:
{
  "breakpoint": "descricao curta do momento critico",
  "ideal_reply": "mensagem WhatsApp curta que o agente deveria ter enviado",
  "principle": "principio de vendas em 1 frase",
  "agent": "sdr|closer|followup",
  "quality": 0.0
}
quality: 0-1 o quanto voce confia que essa racionalizacao e util para treinar o prompt.
"""

DISCRIMINATOR_SYSTEM = """Voce compara dois trechos de conversa de vendas WhatsApp B2B.
Um e de um lead WON (fechou ou avancou forte). Outro e LOST (perdeu/esfriou).

Tarefa (self-play discrimination, estilo SPIN):
- Liste 2-4 diferencas concretas de tom, estrutura, pergunta ou CTA.
- Diga o que o lado WON fez que o LOST nao fez.

Responda SOMENTE JSON:
{
  "win_signals": ["..."],
  "loss_signals": ["..."],
  "lesson": "uma frase acionavel para o prompt do agente"
}
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


def _last_assistant_turns(messages: list[dict], n: int = 3) -> list[str]:
    turns = [
        (m.get("content") or "").strip()
        for m in messages
        if m.get("role") == "assistant" and (m.get("content") or "").strip()
    ]
    return turns[-n:]


def _dominant_agent(messages: list[dict]) -> str:
    counts: dict[str, int] = {}
    for m in messages:
        if m.get("role") != "assistant":
            continue
        a = (m.get("agent") or "sdr").lower()
        if a not in AGENTS:
            a = "sdr"
        counts[a] = counts.get(a, 0) + 1
    if not counts:
        return "sdr"
    return max(counts, key=counts.get)


def sample_outcomes(
    *,
    list_leads_by_stage: Callable[..., list[dict]],
    get_messages_for_lead: Callable[..., list[dict]],
    workspace_id: str,
    per_outcome: int = 8,
) -> tuple[list[dict], list[dict]]:
    """Retorna (won_cases, lost_cases) com transcript e metadados."""
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
                    "stage": stage,
                    "agent": _dominant_agent(msgs),
                    "transcript": _transcript(msgs),
                    "assistant_turns": _last_assistant_turns(msgs),
                    "messages": msgs,
                }
            )
    return won_cases, lost_cases


def build_preference_pairs(
    won: list[dict],
    lost: list[dict],
    max_pairs: int = 12,
) -> list[dict]:
    """Pares no formato SPIN: real=won vs generated=lost."""
    pairs: list[dict] = []
    n = min(len(won), len(lost), max_pairs)
    for i in range(n):
        w, l = won[i], lost[i]
        pairs.append(
            {
                "real": {
                    "role": "assistant",
                    "content": w["transcript"],
                    "meta": {
                        "lead_id": w.get("lead_id"),
                        "outcome": "won",
                        "agent": w.get("agent"),
                        "bant": w.get("bant") or {},
                    },
                },
                "generated": {
                    "role": "assistant",
                    "content": l["transcript"],
                    "meta": {
                        "lead_id": l.get("lead_id"),
                        "outcome": "lost",
                        "agent": l.get("agent"),
                        "bant": l.get("bant") or {},
                    },
                },
                "agent": w.get("agent") or l.get("agent") or "sdr",
            }
        )
    return pairs


def run_discriminator(
    client: Any,
    *,
    model: str,
    pair: dict,
) -> dict[str, Any]:
    user = json.dumps(
        {
            "won_transcript": pair["real"]["content"][:2000],
            "lost_transcript": pair["generated"]["content"][:2000],
        },
        ensure_ascii=False,
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": DISCRIMINATOR_SYSTEM},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
        max_tokens=600,
    )
    raw = response.choices[0].message.content or ""
    data = parse_analyst_json(raw)
    return {
        "win_signals": data.get("win_signals") or [],
        "loss_signals": data.get("loss_signals") or [],
        "lesson": data.get("lesson") or data.get("summary") or "",
        "agent": pair.get("agent") or "sdr",
    }


def run_discriminator_batch(
    client: Any,
    *,
    model: str,
    pairs: list[dict],
    limit: int = 6,
) -> list[dict]:
    lessons: list[dict] = []
    for pair in pairs[:limit]:
        try:
            lessons.append(run_discriminator(client, model=model, pair=pair))
        except Exception:
            continue
    return lessons


def rationalize_lost_case(
    client: Any,
    *,
    model: str,
    case: dict,
) -> dict[str, Any] | None:
    user = json.dumps(
        {
            "transcript": case.get("transcript") or "",
            "bant": case.get("bant") or {},
            "name": case.get("name"),
            "company": case.get("company"),
            "agent_hint": case.get("agent") or "sdr",
        },
        ensure_ascii=False,
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": RATIONALIZER_SYSTEM},
            {
                "role": "user",
                "content": (
                    "Racionalize esta conversa perdida e proponha a resposta ideal "
                    "no ponto de ruptura.\n\n" + user
                ),
            },
        ],
        temperature=0.4,
        max_tokens=800,
    )
    raw = response.choices[0].message.content or ""
    data = parse_analyst_json(raw)
    quality = float(data.get("quality") or 0)
    ideal = (data.get("ideal_reply") or "").strip()
    if quality < 0.45 or len(ideal) < 20:
        return None
    agent = (data.get("agent") or case.get("agent") or "sdr").lower()
    if agent not in AGENTS:
        agent = "sdr"
    return {
        "lead_id": case.get("lead_id"),
        "breakpoint": data.get("breakpoint") or "",
        "ideal_reply": ideal,
        "principle": data.get("principle") or "",
        "agent": agent,
        "quality": quality,
        "original_turns": case.get("assistant_turns") or [],
    }


def rationalize_lost_batch(
    client: Any,
    *,
    model: str,
    lost: list[dict],
    limit: int = 8,
) -> list[dict]:
    out: list[dict] = []
    for case in lost[:limit]:
        try:
            r = rationalize_lost_case(client, model=model, case=case)
            if r:
                out.append(r)
        except Exception:
            continue
    return out


def build_analyst_user_payload(
    won: list[dict],
    lost: list[dict],
    current_prompts: dict[str, str],
    *,
    preference_pairs: list[dict] | None = None,
    rationalizations: list[dict] | None = None,
    spin_lessons: list[dict] | None = None,
) -> str:
    def slim(cases: list[dict]) -> list[dict]:
        return [
            {
                "lead_id": c.get("lead_id"),
                "name": c.get("name"),
                "company": c.get("company"),
                "bant": c.get("bant") or {},
                "agent": c.get("agent"),
                "transcript": c.get("transcript"),
            }
            for c in cases[:10]
        ]

    slim_pairs = []
    for p in (preference_pairs or [])[:8]:
        slim_pairs.append(
            {
                "agent": p.get("agent"),
                "real_excerpt": (p["real"]["content"] or "")[:1200],
                "generated_excerpt": (p["generated"]["content"] or "")[:1200],
            }
        )

    payload = {
        "method": "hybrid_SPIN_STaR",
        "won_count": len(won),
        "lost_count": len(lost),
        "won_samples": slim(won),
        "lost_samples": slim(lost),
        "preference_pairs_spin": slim_pairs,
        "rationalizations_star": rationalizations or [],
        "spin_lessons": spin_lessons or [],
        "current_prompts": current_prompts,
        "output_schema": {
            "summary": "string — resumo executivo em PT-BR",
            "insights": [
                {
                    "type": "win_pattern|loss_pattern|objection|timing|tone|self_play|rationalization",
                    "detail": "string",
                    "evidence": "string curta",
                }
            ],
            "suggestions": [
                {
                    "agent": "sdr|closer|followup",
                    "title": "string curta",
                    "rationale": "por que mudar (cite SPIN pair ou STaR principle)",
                    "diff_summary": "o que muda em bullets",
                    "suggested_prompt": "prompt markdown completo",
                    "source": "spin|star|hybrid",
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
    preference_pairs: list[dict] | None = None,
    rationalizations: list[dict] | None = None,
    spin_lessons: list[dict] | None = None,
) -> dict[str, Any]:
    user = build_analyst_user_payload(
        won,
        lost,
        current_prompts,
        preference_pairs=preference_pairs,
        rationalizations=rationalizations,
        spin_lessons=spin_lessons,
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": ANALYST_SYSTEM},
            {
                "role": "user",
                "content": (
                    "Analise os pares SPIN, racionalizacoes STaR e amostras.\n"
                    "Proponha melhorias de prompt fundamentadas nesses sinais.\n"
                    "Garanta suggested_prompt completo para cada agent que valha mudar.\n\n"
                    f"{user}"
                ),
            },
        ],
        temperature=0.35,
        max_tokens=4000,
    )
    raw = response.choices[0].message.content or ""
    return parse_analyst_json(raw)


def run_hybrid_learning(
    client: Any,
    *,
    model: str,
    won: list[dict],
    lost: list[dict],
    current_prompts: dict[str, str],
    mode: str = "hybrid",
    max_pairs: int = 8,
    max_rationalizations: int = 6,
    max_spin_lessons: int = 4,
) -> dict[str, Any]:
    """mode: hybrid | spin | star | classic"""
    mode = (mode or "hybrid").lower()
    pairs: list[dict] = []
    rationalizations: list[dict] = []
    spin_lessons: list[dict] = []

    if mode in ("hybrid", "spin"):
        pairs = build_preference_pairs(won, lost, max_pairs=max_pairs)
        if pairs:
            spin_lessons = run_discriminator_batch(
                client, model=model, pairs=pairs, limit=max_spin_lessons
            )

    if mode in ("hybrid", "star"):
        rationalizations = rationalize_lost_batch(
            client, model=model, lost=lost, limit=max_rationalizations
        )

    if mode == "classic":
        pairs, rationalizations, spin_lessons = [], [], []

    analysis = run_analyst(
        client,
        model=model,
        won=won,
        lost=lost,
        current_prompts=current_prompts,
        preference_pairs=pairs if mode != "classic" else None,
        rationalizations=rationalizations if mode != "classic" else None,
        spin_lessons=spin_lessons if mode != "classic" else None,
    )

    analysis["_meta"] = {
        "mode": mode,
        "pairs": len(pairs),
        "rationalizations": len(rationalizations),
        "spin_lessons": len(spin_lessons),
        "won": len(won),
        "lost": len(lost),
    }
    return analysis


def ensure_meta_protocol(prompt: str) -> str:
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


def export_preference_dataset(pairs: list[dict]) -> list[dict]:
    """Exporta pares no schema SPIN/HF (real / generated com roles)."""
    dataset = []
    for p in pairs:
        dataset.append(
            {
                "real": [
                    {"role": "user", "content": "(contexto de vendas WhatsApp)"},
                    {"role": "assistant", "content": p["real"]["content"]},
                ],
                "generated": [
                    {"role": "user", "content": "(contexto de vendas WhatsApp)"},
                    {"role": "assistant", "content": p["generated"]["content"]},
                ],
                "meta": {
                    "agent": p.get("agent"),
                    "real_outcome": "won",
                    "generated_outcome": "lost",
                },
            }
        )
    return dataset
