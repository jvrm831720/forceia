# Arquitetura ForceIA MVP

## Fluxo principal

1. Lead envia mensagem no WhatsApp
2. Evolution API recebe e dispara webhook para ForceIA
3. Webhook resolve o **workspace** (instance / API key / default)
4. Lead e historico sao carregados do **Supabase** (isolados por tenant)
5. Agente SDR / Closer / Follow-up gera resposta (OpenAI)
6. Stage atualizado (tags `[QUALIFICADO]`, etc.)
7. Resposta enviada via Evolution; opcionalmente sincroniza **Twenty**
8. Job de follow-up reativa leads parados por workspace

## Componentes

| Componente | Papel |
|------------|--------|
| Evolution API | WhatsApp (docker-compose) |
| `webhook_server.py` | Entrada multi-tenant |
| `run_sdr.py` | Runtime dos agentes |
| Supabase | workspaces, leads, messages, events |
| Twenty | People + Opportunities (por workspace ou global) |
| `followup_job.py` / `scheduler.py` | Reativacao automatica |

## Multi-tenant

Cada cliente ForceIA = 1 `workspace` com leads isolados (`workspace_id + phone`).

Ver `docs/MULTI_TENANT.md`.

## Validacao

```bash
cd agents
python validate_mvp.py
```
