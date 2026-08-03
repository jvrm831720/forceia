# ForceIA

**Seu time de vendas de IA que trabalha 24h por menos de 30% do custo de um SDR humano.**

ForceIA e um time de agentes de IA (SDR + Closer + Follow-up + Relatorios) no WhatsApp, com persistencia no **Supabase**.

## Repo

https://github.com/jvrm831720/forceia

## Stack

| Camada | Tecnologia |
|--------|------------|
| WhatsApp | Evolution API |
| Agentes | Python + OpenAI |
| Estados | SDR → Qualified → Closer → Follow-up |
| Banco | Supabase |
| Jobs | Follow-up automatico (cron / scheduler) |
| CRM (fase 2) | Twenty |
| Integracoes (fase 2) | Composio |

## Quick Start

```bash
git clone https://github.com/jvrm831720/forceia.git
cd forceia
cp .env.example .env
# OPENAI_API_KEY + SUPABASE_*

# Schema: cole supabase/schema.sql no SQL Editor do Supabase

docker compose up -d   # Evolution API

cd agents
pip install -r requirements.txt
python run_sdr.py              # teste dialogo
python webhook_server.py       # producao WhatsApp
python followup_job.py --dry-run
```

Docs:
- [Setup](docs/SETUP.md)
- [Supabase](docs/SUPABASE.md)
- [Follow-up jobs](docs/FOLLOWUP.md)
- [Arquitetura](docs/ARCHITECTURE.md)

## Estagios

`sdr` → `qualified` → `closer` → `won` / `lost` (+ `followup`)

Tags: `[QUALIFICADO]`, `[FECHADO]`, `[PERDIDO]`, `[FOLLOWUP]`

## Follow-up automatico

Leads sem resposta ha N dias recebem mensagem do agente Follow-up.

```bash
python followup_job.py --days 5
python scheduler.py --hours 6
```

## Precos (produto)

| Plano | Mensal |
|-------|--------|
| Starter | R$ 3.497 |
| Completo | R$ 4.497 |
| Enterprise | a partir de R$ 5.997 |

Setup: R$ 5.900

---

ForceIA - A forca de vendas que nunca dorme.
