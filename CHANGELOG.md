# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [1.10.0]

### Adicionado
- **Integrações Fase 2+3 — tools no Closer**
  - `integrations/tools/{calendar,email,notify}.py`
  - `integrations/actions.py`
  - Nó LangGraph `actions` (`parse → actions → route → persist`)
  - META `intent=schedule` + `meeting.{title,start,duration_minutes}`
  - Handoff → Slack se conectado
  - Prompt Closer: seção de agendamento
  - Testes: `tests/test_actions.py`

## [1.9.0]

### Adicionado
- **Camada de integrações (Fase 0 + 1)**
  - ADR: `docs/INTEGRATIONS.md`
  - `agents/integrations/` — `base`, `registry`, `composio_client`
  - Sessão Composio por workspace
  - API admin de integrações
  - Testes: `agents/tests/test_integrations.py`

## [1.8.0]

### Adicionado
- Notas internas, timeline de eventos, pausar agente / handoff humano
