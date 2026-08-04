# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [2.2.0] — Prioridade 4 · Confiabilidade e confiança

### Adicionado
- **Guardrails** (`agents/guardrails.py`)
  - Instrução no system prompt: nunca inventar preço/prazo
  - Scan + sanitização pós-resposta no runtime
  - `POST /api/workspaces/{slug}/guardrails/scan`
  - Evento `guardrail_enforced`
- **A/B de prompts** (`agents/ab_testing.py`)
  - Variante A/B estável por lead (hash phone)
  - Override opcional `sdr_b` / `closer_b` / `followup_b`
  - `GET /api/workspaces/{slug}/ab-report` (conversão + lift)
  - Env `FORCEIA_AB_TESTING`
- **Handoff humano suave** (`agents/handoff.py`)
  - Resumo BANT + intent + últimas msgs
  - Pausa agente + notifica WhatsApp (`handoff_phone` / `owner_phone`)
  - `POST /api/workspaces/{slug}/leads/{id}/handoff`
  - Wire automático quando META `handoff: true`
- Docs: `docs/TRUST.md` · testes `agents/tests/test_trust.py`
- `trust_routes.py` montado no admin

## [2.1.0] — Prioridade 3 · Experiência de produto

- Performance dashboard (reuniões + IA vs humano)
- Relatório WhatsApp para o dono
- Playground de simulação
- UI premium (painel de time de vendas)

## [2.0.0] — Prioridade 1 · Playbook

- Playbook por workspace no system prompt + aba no console

## [1.9.0] — Integrações Composio

## [1.8.0] — Notes, timeline, pause agente

## [1.7.x] — Lead detail + transcript

## [1.6.0] — Auth JWT
