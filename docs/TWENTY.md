# Integracao Twenty CRM - ForceIA

Sincroniza leads do Supabase com **People** e **Opportunities** no Twenty.

## 1. Subir o Twenty

Opcao A - Docker (self-hosted):

```bash
# Veja https://github.com/twentyhq/twenty e docs.twenty.com
# Exemplo tipico:
bash <(curl -sL https://raw.githubusercontent.com/twentyhq/twenty/main/packages/twenty-docker/scripts/install.sh)
```

Opcao B - Twenty Cloud: crie workspace em https://twenty.com

## 2. API Key

No Twenty:
1. Settings → APIs & Webhooks (ou Developers)
2. Crie uma API Key
3. Copie a URL base da API (ex: `https://api.twenty.com` ou `http://localhost:3000`)

No `.env` da ForceIA:

```env
TWENTY_API_URL=https://sua-instancia-twenty
TWENTY_API_KEY=seu_token
TWENTY_CREATE_OPP_ALWAYS=true
```

## 3. Mapeamento de estagios

ForceIA → Twenty (padrao, customizavel):

| ForceIA | Twenty stage |
|---------|--------------|
| sdr | NEW |
| qualified | SCREENING |
| closer | MEETING |
| followup | SCREENING |
| won | CUSTOMER |
| lost | REJECTED |

Override no `.env`:

```env
TWENTY_STAGE_SDR=NEW
TWENTY_STAGE_QUALIFIED=SCREENING
TWENTY_STAGE_CLOSER=MEETING
TWENTY_STAGE_FOLLOWUP=SCREENING
TWENTY_STAGE_WON=CUSTOMER
TWENTY_STAGE_LOST=REJECTED
```

**Importante:** os nomes de stage devem existir no pipeline do seu workspace Twenty. Ajuste conforme a versao/configuracao.

## 4. O que e sincronizado

| Evento ForceIA | Twenty |
|----------------|--------|
| Novo lead (WhatsApp) | Cria **Person** (telefone) |
| Stage muda | Cria/atualiza **Opportunity** + stage |
| Job `sync_twenty_job.py` | Reprocessa leads em lote |

IDs ficam em `leads.metadata`:
- `twenty_person_id`
- `twenty_opportunity_id`

## 5. Comandos

```bash
cd agents

# Sync em lote
python sync_twenty_job.py
python sync_twenty_job.py --dry-run

# O sync automatico ja roda em handle_incoming quando:
# - lead e criado
# - stage muda
# - lead ainda nao tem twenty_person_id
```

## 6. Troubleshooting

| Sintoma | Acao |
|---------|------|
| `Twenty nao configurado` | Preencha TWENTY_API_URL e TWENTY_API_KEY |
| GraphQL errors de stage | Ajuste TWENTY_STAGE_* para os stages reais do workspace |
| Person duplicado | Filtro de telefone varia por versao; rode sync e confira metadata |
| 401 | API key invalida ou URL errada (precisa terminar sem /graphql) |

Eventos no Supabase: `twenty_synced`, `twenty_sync_error`.

## 7. Notas de compatibilidade

A API GraphQL do Twenty evolui entre versoes. Se mutations falharem:

1. Abra o GraphQL playground do seu Twenty
2. Confira nomes de inputs (`PersonCreateInput`, stages enum)
3. Ajuste queries em `agents/twenty_client.py`

O cliente foi escrito de forma tolerante (try/fallback na busca por telefone).
