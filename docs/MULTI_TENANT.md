# Multi-tenant ForceIA

Cada **cliente ForceIA** e um `workspace` isolado no Supabase.

## Modelo

```
workspaces
  └── leads (unique por workspace + phone)
        └── messages
  └── events
```

Credenciais **por workspace** (opcionais; caem no .env global se vazias):
- Evolution (instance, url, key)
- Twenty (url, key)
- OpenAI (key, model)
- Follow-up (dias / horas)

## Criar cliente

```bash
cd agents
python create_workspace.py --name "Clinica Sol" --slug clinica-sol --instance clinica-sol-wa
```

Guarde o `api_key` retornado.

Ou no SQL:

```sql
insert into workspaces (name, slug, evolution_instance)
values ('Clinica Sol', 'clinica-sol', 'clinica-sol-wa');
```

## Roteamento do webhook

O webhook resolve o tenant nesta ordem:

1. Header `X-Workspace-Key: <api_key>`
2. `instance` no body/query da Evolution
3. `DEFAULT_WORKSPACE_SLUG` no `.env`

Exemplo Evolution webhook URL:

```
https://sua-api.com/webhook/evolution?instance=clinica-sol-wa
```

## Isolamento

- Lead do workspace A nunca aparece no B (unique `workspace_id + phone`)
- Follow-up job pode rodar `--workspace clinica-sol` ou `--all`
- Twenty/OpenAI/Evolution podem ser diferentes por cliente

## Jobs

```bash
python followup_job.py --workspace clinica-sol
python followup_job.py --all
python sync_twenty_job.py --workspace clinica-sol
```

## Migracao

Se voce ja tinha o schema antigo:

1. Rode `supabase/migrate_multitenant.sql`
2. Confira o workspace `default`
3. Atualize o codigo e o `.env` com `DEFAULT_WORKSPACE_SLUG=default`

## Onboarding de um cliente novo (checklist)

1. `create_workspace.py`
2. Criar instancia Evolution com o mesmo `evolution_instance`
3. Apontar webhook da instancia para a ForceIA
4. (Opcional) Twenty proprio do cliente → preencher `twenty_api_*` no workspace
5. Testar mensagem no WhatsApp do cliente
