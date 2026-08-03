# Setup ForceIA MVP (Supabase + Twenty)

## 1. Supabase

Siga `docs/SUPABASE.md`:
1. Crie o projeto
2. Rode `supabase/schema.sql`
3. Preencha `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` no `.env`

## 2. Twenty CRM

Siga `docs/TWENTY.md`:
1. Suba o Twenty (Docker ou Cloud)
2. Gere API Key
3. Preencha `TWENTY_API_URL` e `TWENTY_API_KEY`
4. Ajuste `TWENTY_STAGE_*` se o pipeline do seu workspace for diferente

## 3. Variaveis

```bash
cp .env.example .env
```

Obrigatorio:
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

WhatsApp:
- `EVOLUTION_API_KEY` / `EVOLUTION_INSTANCE`

CRM:
- `TWENTY_API_URL` / `TWENTY_API_KEY`

## 4. Evolution API

```bash
docker compose up -d
```

Webhook → `https://SEU_TUNEL/webhook/evolution`

## 5. Agentes

```bash
cd agents
pip install -r requirements.txt
python webhook_server.py
python run_sdr.py
python followup_job.py --dry-run
python sync_twenty_job.py --dry-run
```

## 6. Fluxo completo

1. Lead manda WhatsApp
2. Webhook → agente (SDR/Closer/Follow-up)
3. Supabase grava lead + mensagens
4. Twenty recebe Person + Opportunity (stage espelhado)
5. Job de follow-up reativa parados
6. Job `sync_twenty_job` pode reconciliar em lote
