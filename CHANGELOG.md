# Changelog

## 2.6.0 — 2026-08-04

### P2 — Console badges, bulk list building, closer tool registry

- `lead_badges.py`: badges score/ICP/health/intent + `summarize_workspace_intelligence`
- `list_builder.py`: import em massa com normalização BR e sync Twenty opcional
- `tools/closer_registry.py`: registry formal (schedule / proposal / handoff) executado a partir do META
- `p2_routes.py` montado no admin: leads-enriched, metrics-intel, bulk, tools
- Console: tabela com badges, chips Hot/At-risk/Ready, UI de bulk import (JSON/CSV)
- Graph: `_node_actions` usa registry (fallback para `closer_tools` P0)
- Mount de elite/skills/product/trust routes no `admin_server`

## 2.5.0 — 2026-08-04

### P1 — Turn policy, memória e intent routing

- `turn_policy.py`: objetivo por stage, limite de perguntas, trim WhatsApp, handoff por 2+ objeções
- Contexto de lead anti-repetição (BANT conhecido vs faltante + objeções)
- Skills condicionais por message_count / stage / tier
- Intent guia agente e stage no LangGraph (`ready_to_buy` → closer/qualified)
- System prompt recebe agent + history (turn policy + skills corretos)

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
