# ForceIA

**Time de vendas de IA multi-tenant** — WhatsApp + SDR/Closer/Follow-up + Supabase + Twenty.

Repo: https://github.com/jvrm831720/forceia

## Validar o MVP

```bash
git clone https://github.com/jvrm831720/forceia.git
cd forceia
cp .env.example .env
# Preencha SUPABASE_* e OPENAI_API_KEY
# Rode supabase/schema.sql no SQL Editor

cd agents
pip install -r requirements.txt
python create_workspace.py --name Default --slug default --instance forceia
python validate_mvp.py          # smoke test
python run_sdr.py               # dialogo local
```

## Stack

| Camada | Tecnologia |
|--------|------------|
| WhatsApp | Evolution API |
| Agentes | Python + OpenAI |
| Banco | Supabase (multi-tenant) |
| CRM | Twenty |
| Jobs | Follow-up + sync Twenty |

## Comandos uteis

```bash
python webhook_server.py
python followup_job.py --all --dry-run
python scheduler.py --hours 6 --all
python sync_twenty_job.py --workspace default
```

Docs: [Setup](docs/SETUP.md) · [Validacao no SETUP](docs/SETUP.md) · [Multi-tenant](docs/MULTI_TENANT.md)

---
ForceIA - A forca de vendas que nunca dorme.
