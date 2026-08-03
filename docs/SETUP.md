# Setup ForceIA (multi-tenant)

## Checklist de validacao

1. Schema Supabase (`schema.sql` ou `migrate_multitenant.sql`)
2. `.env` com Supabase + OpenAI
3. Workspace `default` criado
4. `python validate_mvp.py` sem FAIL
5. `python run_sdr.py` responde no terminal
6. (Opcional) Evolution + webhook WhatsApp
7. (Opcional) Twenty API key

## 1. Supabase

Rode `supabase/schema.sql` e depois:

```bash
cd agents
pip install -r requirements.txt
python create_workspace.py --name "Default" --slug default --instance forceia
```

## 2. .env

```bash
cp .env.example .env
# SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, OPENAI_API_KEY
# DEFAULT_WORKSPACE_SLUG=default
```

Coloque o `.env` na **raiz** do repo (nao so em agents/).

## 3. Validar codigo + banco

```bash
cd agents
python validate_mvp.py
```

## 4. Teste de dialogo (sem WhatsApp)

```bash
python run_sdr.py
```

## 5. Evolution (WhatsApp)

```bash
# na raiz
docker compose up -d
```

1. http://localhost:8080 — crie instancia `forceia` (mesmo nome do workspace)
2. QR Code
3. Webhook: `https://SEU_TUNEL/webhook/evolution?instance=forceia`
4. `python webhook_server.py`

**Nota:** o Postgres do compose cria o DB `evolution` no primeiro start (arquivo `docker/init-evolution-db.sql`). Se o volume ja existia sem esse DB, crie manualmente:

```sql
CREATE DATABASE evolution;
```

## 6. Jobs

```bash
python followup_job.py --dry-run
python scheduler.py --once --all
python sync_twenty_job.py --dry-run
```

Docs: [Multi-tenant](MULTI_TENANT.md) · [Supabase](SUPABASE.md) · [Twenty](TWENTY.md) · [Follow-up](FOLLOWUP.md)
