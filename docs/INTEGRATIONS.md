# Integrações — ForceIA

ADR e guia da camada de integrações (Fase 0 + Fase 1).

## Decisão (ADR)

### Contexto

ForceIA já tem integrações **first-party**:

- WhatsApp via Evolution API
- CRM via Twenty (GraphQL por workspace)
- OpenAI / LangGraph / Langfuse

Clientes brasileiros de B2B pedem Calendar (agendar demo), e-mail paralelo, Slack de handoff e CRMs alternativos (HubSpot, Pipedrive, RD Station). Reimplementar OAuth e APIs de cada app não escala.

### Decisão

1. **Composio** como provider de toolkits autenticados (OAuth gerenciado, 1000+ apps).
2. **Abstração própria** em `agents/integrations/` — Composio é *um* provider, não o produto.
3. **Identidade multi-tenant**: `user_id` Composio = `workspace:{workspace_id}` (ou o UUID do workspace).
4. **Sessão persistida** em `workspaces.metadata.composio_session_id`.
5. **Twenty e Evolution permanecem first-party** — não migram para Composio na v1.
6. **Allowlist de toolkits** por env (`FORCEIA_COMPOSIO_TOOLKITS`) e, depois, por plano.

### Consequências

- Feature flag: `FORCEIA_COMPOSIO=1` + `COMPOSIO_API_KEY`.
- Sem chave / SDK ausente → integrações desabilitadas com degradação graciosa (WhatsApp continua).
- Tools de agente (Calendar, Gmail…) entram só nos nós certos do LangGraph (Closer / Follow-up), nunca no SDR genérico.
- Toda execução de tool deve gerar `events.type = tool_executed` (Fase 3+).

## Arquitetura

```
agents/integrations/
  base.py              # Protocol IntegrationProvider + tipos
  registry.py          # catálogo + status por workspace
  composio_client.py   # provider Composio (sessão, authorize, execute)
  tools/               # (Fase 2+) wrappers de domínio
```

```
Workspace ForceIA  ──user_id──►  Composio Session
       │                              │
       │ metadata.composio_session_id │
       ▼                              ▼
  workspace_integrations?      connected_accounts
  (opcional, tabela)           (Calendar, Gmail, Slack…)
```

## Fase 1 — API interna

| Função | Descrição |
|--------|-----------|
| `is_composio_enabled()` | Flag + API key presentes |
| `get_or_create_session(workspace_id)` | Cria/reusa sessão; grava session_id no metadata |
| `authorize(workspace_id, toolkit)` | Retorna URL OAuth / Connect Link |
| `list_connected(workspace_id)` | Contas conectadas do user |
| `execute_tool(workspace_id, tool, args)` | Executa tool autenticada |
| `list_available_toolkits()` | Allowlist configurada |

## Admin (mínimo Fase 1)

```
GET  /api/workspaces/{slug}/integrations
POST /api/workspaces/{slug}/integrations/{toolkit}/connect
POST /api/workspaces/{slug}/integrations/{toolkit}/disconnect
```

## Env

```bash
FORCEIA_COMPOSIO=1
COMPOSIO_API_KEY=...
# allowlist separada por vírgula
FORCEIA_COMPOSIO_TOOLKITS=googlecalendar,gmail,slack,outlook
# opcional: callback após OAuth
FORCEIA_COMPOSIO_CALLBACK_URL=https://app.forceia.com.br/integrations/callback
```

## Fora de escopo (Fase 1)

- UI React completa de settings de integração (só API)
- Tool calling dentro do LangGraph (Fase 3)
- Triggers inbound Composio (Fase 5)
- Substituir Twenty/Evolution

## Ver também

- [TWENTY.md](TWENTY.md) — CRM first-party
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [MULTI_TENANT.md](MULTI_TENANT.md)
