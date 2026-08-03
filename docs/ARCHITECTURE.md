# Arquitetura ForceIA MVP

## Fluxo principal

1. Lead envia mensagem no WhatsApp
2. Evolution API recebe e dispara webhook para ForceIA
3. Webhook identifica o lead e carrega historico
4. Agente SDR (ou Closer/Follow-up conforme estagio) gera resposta
5. Resposta e enviada de volta via Evolution API
6. Dados do lead sao atualizados (memoria local no MVP; Twenty no futuro)

## Componentes

### Evolution API
- Gerencia conexao WhatsApp (Baileys ou Cloud API)
- Webhooks de mensagens recebidas
- API de envio de texto/midia

### Agentes (Python)
- `run_sdr.py`: logica do SDR + envio WhatsApp
- `webhook_server.py`: recebe eventos e roteia
- Prompts em `config/prompts/`

### CRM (fase 2)
- Twenty como painel e fonte de verdade do pipeline
- Sincronizacao lead <-> oportunidade

### Integracoes (fase 2+)
- Composio para Calendar, Gmail, etc.
- Calendly para agendamento automatico

## Proximos passos tecnicos

1. Conectar webhook da Evolution no `webhook_server`
2. Persistir conversas em Postgres/Redis
3. Maquina de estados (SDR -> Closer -> Follow-up)
4. Integrar Twenty via API GraphQL
5. Multi-tenant (um workspace por cliente ForceIA)
