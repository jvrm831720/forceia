# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

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

## [1.5.0]

### Adicionado
- Langfuse observabilidade

## [1.4.0]

### Adicionado
- LangGraph orquestrador do funil

## [1.3.0]

### Adicionado
- STaR + SPIN no ciclo de learning

## [1.2.0]

### Adicionado
- Auto-melhoria assistida

## [1.1.0]

### Adicionado
- Camada intelligence BANT/META

## [1.0.0]

### Adicionado
- Painel admin, webhook, testes, Docker
