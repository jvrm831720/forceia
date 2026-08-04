# Prioridade 4 — Confiabilidade e confiança

## 13. Guardrails

**Arquivo:** `agents/guardrails.py`

1. Instrução no system prompt (`format_guardrails_for_prompt`) — nunca inventar preço/prazo.
2. Scan + sanitização pós-resposta (`enforce_guardrails`) no runtime legado.

Se o playbook tiver `pricing.range`, valores que batem com o range são permitidos.
Caso contrário, a resposta é reescrita com fallback honesto.

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -d '{"text":"Fecha por R$ 999 ainda hoje"}' \
  http://localhost:8100/api/workspaces/demo/guardrails/scan
```

Evento: `guardrail_enforced`.

## 14. A/B de prompts

**Arquivo:** `agents/ab_testing.py`

- Cada lead recebe variante **A** ou **B** (hash estável do phone).
- Variante B usa override `agent_prompt_overrides` com agent `sdr_b` / `closer_b` / `followup_b` se existir.
- Conversão = stage ∈ `qualified|closer|won`.

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8100/api/workspaces/demo/ab-report
```

Env: `FORCEIA_AB_TESTING=0` desliga (todos em A).

## 15. Handoff humano suave

**Arquivo:** `agents/handoff.py`

Quando META `handoff: true` ou API manual:

1. Gera resumo (BANT, intent, últimas msgs)
2. Pausa o agente
3. Notifica WhatsApp em `metadata.handoff_phone` (fallback `owner_phone`)

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -d '{"reason":"Lead pediu gerente","notify":true}' \
  http://localhost:8100/api/workspaces/demo/leads/{id}/handoff
```

Env: `FORCEIA_HANDOFF_PHONE`.
