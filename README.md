# ForceIA

**Seu time de vendas de IA que trabalha 24h por menos de 30% do custo de um SDR humano.**

ForceIA e um time de agentes de IA (SDR + Closer + Follow-up + Relatorios) no WhatsApp, com persistencia no **Supabase**.

## Repo

https://github.com/jvrm831720/forceia

## Stack

| Camada | Tecnologia |
|--------|------------|
| WhatsApp | Evolution API |
| Agentes | Python + OpenAI (prompts estilo SalesGPT) |
| Estados | Maquina SDR → Qualified → Closer → Follow-up |
| Banco | **Supabase** (Postgres) |
| CRM (fase 2) | Twenty |
| Integracoes (fase 2) | Composio |

## Quick Start

```bash
git clone https://github.com/jvrm831720/forceia.git
cd forceia
cp .env.example .env
# Preencha OPENAI_API_KEY + SUPABASE_* 

# 1) Schema no Supabase (SQL Editor)
#    cole o conteudo de supabase/schema.sql

# 2) WhatsApp (opcional no primeiro teste)
docker compose up -d

# 3) Agente
cd agents
pip install -r requirements.txt
python run_sdr.py
```

Docs:
- [Setup](docs/SETUP.md)
- [Supabase](docs/SUPABASE.md)
- [Arquitetura](docs/ARCHITECTURE.md)

## Estagios do lead

`sdr` → `qualified` → `closer` → `won` / `lost`  
(com desvio para `followup`)

Tags na resposta do agente disparam a troca de estagio: `[QUALIFICADO]`, `[FECHADO]`, `[PERDIDO]`, `[FOLLOWUP]`.

## Precos (produto)

| Plano | Mensal |
|-------|--------|
| Starter | R$ 3.497 |
| Completo | R$ 4.497 |
| Enterprise | a partir de R$ 5.997 |

Setup: R$ 5.900

---

ForceIA - A forca de vendas que nunca dorme.
