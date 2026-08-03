# Setup ForceIA MVP (com Supabase)

## 1. Supabase

Siga `docs/SUPABASE.md`:
1. Crie o projeto
2. Rode `supabase/schema.sql`
3. Preencha `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` no `.env`

## 2. Variaveis

```bash
cp .env.example .env
```

Obrigatorio:
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Para WhatsApp:
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`

Follow-up (opcional):
- `FOLLOWUP_STALE_DAYS=5`
- `FOLLOWUP_MIN_HOURS=48`

## 3. Evolution API (WhatsApp)

```bash
docker compose up -d
```

1. Abra http://localhost:8080
2. Crie instancia (ex: `forceia`)
3. Conecte o QR Code
4. Webhook de mensagens → `https://SEU_TUNEL/webhook/evolution`
   (use ngrok em dev: `ngrok http 8000`)

## 4. Agentes

```bash
cd agents
pip install -r requirements.txt
python webhook_server.py
```

Teste so o dialogo (sem WhatsApp):

```bash
python run_sdr.py
```

## 5. Job de Follow-up

```bash
# Simular
python followup_job.py --dry-run

# Enviar de verdade
python followup_job.py --days 5

# Loop a cada 6h
python scheduler.py --hours 6 --days 5
```

Detalhes em `docs/FOLLOWUP.md`.

## 6. Fluxo esperado

1. Lead manda WhatsApp
2. Evolution → webhook ForceIA
3. Lead criado/atualizado no Supabase (`stage=sdr`)
4. Agente SDR responde
5. Se a resposta tiver `[QUALIFICADO]`, stage vira `qualified` e o Closer assume
6. Se o lead ficar X dias sem responder, o **followup_job** reativa automaticamente
