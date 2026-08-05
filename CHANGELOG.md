# Changelog

## 2.4.0 — 2026-08-04

### P0 — LangGraph wire (elite + trust)

- **prepare**: enrichment automático, variante A/B estável, detecção de intent lexical e lead score antes do LLM
- **generate**: resolve prompt A/B (`agent_b` override) e registra `ab_exposure`
- **parse**: `enforce_guardrails` (preço/prazo), intent refinado META+lexical, score/tier no metadata, auto-qualify por BANT + score/intent
- **actions**: `execute_closer_actions` (calendar + proposta) além de `run_agent_actions`; `wants_meeting` quando intent=`ready_to_buy`
- **persist**: `execute_handoff` completo (pausa agente + notifica humano via WhatsApp)

Flags relevantes (sem mudança de contrato):
- `FORCEIA_USE_GRAPH` (default 1)
- `FORCEIA_AB_TESTING` (default 1)

## Anteriores

Ver commits e README para histórico do MVP multi-tenant, playbook, skills e learning STaR/SPIN.
