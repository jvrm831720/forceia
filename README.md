# ForceIA

**Time de vendas de IA multi-tenant** — um workspace por cliente.

WhatsApp (Evolution) + Agentes (SDR/Closer/Follow-up) + Supabase + Twenty CRM.

## Repo

https://github.com/jvrm831720/forceia

## Multi-tenant

Cada cliente ForceIA = 1 linha em `workspaces`:
- Instancia WhatsApp propria
- Leads isolados
- Credenciais Twenty/OpenAI opcionais por tenant
- Follow-up e sync por workspace ou `--all`

```bash
python create_workspace.py --name "Cliente X" --slug cliente-x
python followup_job.py --workspace cliente-x
python sync_twenty_job.py --all
```

## Quick Start

```bash
git clone https://github.com/jvrm831720/forceia.git
cd forceia && cp .env.example .env
# SUPABASE_* + OPENAI_API_KEY
# Rode supabase/schema.sql

cd agents && pip install -r requirements.txt
python create_workspace.py --name Default --slug default --instance forceia
python run_sdr.py
python webhook_server.py
```

Docs: [Setup](docs/SETUP.md) · [Multi-tenant](docs/MULTI_TENANT.md) · [Supabase](docs/SUPABASE.md) · [Twenty](docs/TWENTY.md) · [Follow-up](docs/FOLLOWUP.md)

## Precos

| Plano | Mensal |
|-------|--------|
| Starter | R$ 3.497 |
| Completo | R$ 4.497 |
| Enterprise | a partir de R$ 5.997 |

Setup: R$ 5.900

---
ForceIA - A forca de vendas que nunca dorme.
