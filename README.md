# ForceIA

**Seu time de vendas de IA que trabalha 24h por menos de 30% do custo de um SDR humano.**

Time de agentes (SDR + Closer + Follow-up) no WhatsApp, com **Supabase** + **Twenty CRM**.

## Repo

https://github.com/jvrm831720/forceia

## Stack

| Camada | Tecnologia |
|--------|------------|
| WhatsApp | Evolution API |
| Agentes | Python + OpenAI |
| Estados | SDR → Qualified → Closer → Follow-up |
| Banco | Supabase |
| CRM | Twenty (People + Opportunities) |
| Jobs | Follow-up + sync Twenty |

## Quick Start

```bash
git clone https://github.com/jvrm831720/forceia.git
cd forceia
cp .env.example .env
# OPENAI_API_KEY, SUPABASE_*, TWENTY_*

# Schema Supabase: supabase/schema.sql
docker compose up -d

cd agents && pip install -r requirements.txt
python run_sdr.py
python webhook_server.py
python followup_job.py --dry-run
python sync_twenty_job.py --dry-run
```

Docs:
- [Setup](docs/SETUP.md)
- [Supabase](docs/SUPABASE.md)
- [Twenty CRM](docs/TWENTY.md)
- [Follow-up](docs/FOLLOWUP.md)

## Sync Twenty

- Novo lead / mudanca de stage → sync automatico
- `python sync_twenty_job.py` → lote
- IDs em `leads.metadata.twenty_person_id` / `twenty_opportunity_id`

## Precos (produto)

| Plano | Mensal |
|-------|--------|
| Starter | R$ 3.497 |
| Completo | R$ 4.497 |
| Enterprise | a partir de R$ 5.997 |

Setup: R$ 5.900

---

ForceIA - A forca de vendas que nunca dorme.
