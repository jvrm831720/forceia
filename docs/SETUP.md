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

## 5. Fluxo esperado

1. Lead manda WhatsApp
2. Evolution → webhook ForceIA
3. Lead criado/atualizado no Supabase (`stage=sdr`)
4. Agente SDR responde
5. Se a resposta tiver `[QUALIFICADO]`, stage vira `qualified` e o Closer assume nas proximas mensagens
