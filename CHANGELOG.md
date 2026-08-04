# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [2.0.0]

### Adicionado
- **Playbook por workspace (Prioridade 1 — especialização dos agentes)**
  - Módulo `agents/playbook.py` (schema, normalize, completeness, format para prompt)
  - Coluna `workspaces.playbook` (`supabase/playbook.sql`) com fallback `metadata.playbook`
  - Injeção automática no system prompt (SDR / Closer / Follow-up) via `build_system_prompt`
  - API:
    - `GET  /api/workspaces/{slug}/playbook`
    - `PUT  /api/workspaces/{slug}/playbook`
    - `GET  /api/workspaces/{slug}/playbook/template`
  - Aba **Playbook** no console React (ICP, pricing, cases, objeções, tom, FAQ)
  - Score de completude 0–100 (`ready` ≥ 50)
  - Docs: `docs/PLAYBOOK.md`
  - Testes: `agents/tests/test_playbook.py`

## [1.9.0]

### Adicionado
- **Camada de integrações (Fase 0 + 1)**
  - ADR: `docs/INTEGRATIONS.md`
  - `agents/integrations/` — `base`, `registry`, `composio_client`
  - Sessão Composio por workspace (`metadata.composio_session_id`)
  - Allowlist `FORCEIA_COMPOSIO_TOOLKITS` (Calendar, Gmail, Slack, Outlook…)
  - API admin:
    - `GET  /api/workspaces/{slug}/integrations`
    - `POST /api/workspaces/{slug}/integrations/{toolkit}/connect`
    - `POST /api/workspaces/{slug}/integrations/{toolkit}/disconnect`
    - `GET  /api/integrations/health`
  - `update_workspace_metadata` em `db.py`
  - Testes: `agents/tests/test_integrations.py`
  - Migration opcional: `supabase/integrations.sql`

## [1.8.0]

### Adicionado
- **Notas internas no lead**
  - `POST /api/workspaces/{slug}/leads/{lead_id}/notes`
  - Evento `internal_note` + espelho em `metadata.notes`
  - UI: compositor + lista no detalhe do lead
- **Timeline de eventos do lead**
  - `list_events_for_lead` + incluso em `GET .../leads/{id}`
  - `GET /api/workspaces/{slug}/leads/{lead_id}/events`
  - Painel no detalhe com tipo, resumo e horário
- **Assumir conversa / pausar agente**
  - `POST /api/workspaces/{slug}/leads/{lead_id}/pause` `{paused, reason}`
  - `metadata.agent_paused` / `human_takeover`
  - Runtime (`run_sdr`, LangGraph, follow-up) grava msg do lead e **não** responde
  - UI: botão Assumir/Retomar + badge "humano" / ⏸ na lista

## [1.7.1]

### Adicionado
- Melhorias na tela de lead + transcript (filtros, PATCH stage, cores por agente, auto-scroll, WhatsApp)

## [1.7.0]

### Adicionado
- Tela de lead + transcript (`GET .../leads/{id}`)

## [1.6.1]

### Adicionado
- Política de senha forte no login JWT

## [1.6.0]

### Adicionado
- Auth JWT no painel admin
