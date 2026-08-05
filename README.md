# ForceIA

**Time de vendas de IA multi-tenant** — WhatsApp + SDR / Closer / Follow-up + Supabase + Twenty.

> A força de vendas que nunca dorme.

![CI](https://github.com/jvrm831720/forceia/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Repo: https://github.com/jvrm831720/forceia

**Mapa completo do código (desde o dia 01):** [CODEBASE.md](CODEBASE.md)

---

## O que é

Agentes de IA (SDR, Closer e Follow-up) atendem leads no WhatsApp, qualificam com
BANT, avançam o funil por uma máquina de estados e sincronizam com o CRM Twenty.
Cada cliente é um **workspace** isolado no Supabase, com **playbook** próprio
(ICP, pricing, cases, tom) para os agentes se comportarem como especialistas do vertical.

## Stack

| Camada | Tecnologia |
|--------|------------|
| WhatsApp | Evolution API |
| Agentes | Python + OpenAI + LangGraph |
| Banco | Supabase (multi-tenant) |
| CRM | Twenty (opcional, por workspace) |
| Integrações | Composio (Calendar, LinkedIn…) |
| Jobs | Follow-up + sync Twenty |
| Painel | FastAPI admin + console React |
| Dashboard cliente | Next.js 14 em `dashboard/` |

## Quickstart

```bash
git clone https://github.com/jvrm831720/forceia.git
cd forceia
cp .env.example .env
# Preencha SUPABASE_*, OPENAI_API_KEY e ADMIN_TOKEN

# Rode supabase/schema.sql no SQL Editor do Supabase

cd agents
pip install -r requirements.txt
python create_workspace.py --name Default --slug default --instance forceia
python validate_mvp.py          # smoke test
python run_sdr.py               # diálogo local
```

Com `make` (na raiz):

```bash
make install-dev   # dependências
make validate      # smoke test
make test          # testes unitários (sem Supabase/OpenAI)
make webhook       # webhook em :8000
make admin         # painel admin em :8100
```

## Painel admin

```bash
# defina ADMIN_TOKEN no .env
make admin         # http://localhost:8100
```

KPIs, funil de pipeline, leads, eventos, playbook e criação de workspace. Veja [docs/ADMIN.md](docs/ADMIN.md).

## Dashboard cliente (Vercel)

O Painel Cliente (Next.js) vive em **`dashboard/`**.

Na Vercel (Settings → General):

| Campo | Valor |
|--------|--------|
| **Framework Preset** | Next.js |
| **Root Directory** | `dashboard` |
| **Install Command** | `npm ci` |
| **Build Command** | `npm run build` |
| **Output Directory** | *(vazio — gerenciado pelo Next.js)* |
| **Node.js Version** | 20.x |

```bash
cd dashboard
npm ci
npm run build   # deve finalizar com sucesso
npm run dev
```

**Importante:** não use a raiz do repositório como Root Directory. Não há `package.json` de frontend na raiz (monorepo Python + `dashboard/` + `web/`). Deploys com Root Directory `/` falham em 1–2 segundos.

Detalhes: [dashboard/README.md](dashboard/README.md).

## Deploy 24/7

```bash
# Infra (Evolution + Postgres + Redis) + app (webhook + admin)
docker compose --profile app up -d --build
```

Guia completo (VPS, Railway/Render, HTTPS, cron): [docs/DEPLOY.md](docs/DEPLOY.md).

## Comandos úteis

```bash
cd agents
python webhook_server.py                    # webhook multi-tenant
python admin_server.py                      # painel admin
python followup_job.py --all --dry-run      # follow-up (simulação)
python scheduler.py --hours 6 --all         # scheduler em processo
python sync_twenty_job.py --workspace default
```

## Testes e qualidade

```bash
ruff check agents   # lint
pytest              # testes unitários, sem serviços externos
```

CI roda `ruff` + `pytest` em Python 3.11 e 3.12 a cada push/PR.

## Estrutura

```
CODEBASE.md        mapa vivo do repositório (comece por aqui)
agents/            agentes, webhook, painel admin, jobs e testes
dashboard/         Painel Cliente Next.js (deploy Vercel → Root Directory: dashboard)
web/               console React legado (Vite)
config/prompts/    prompts editáveis (sdr / closer / followup)
supabase/          schema + migrations
docker/            init do Postgres da Evolution
docs/              documentação temática
```

## Documentação

**[CODEBASE.md](CODEBASE.md)** (mapa completo) ·
[Setup](docs/SETUP.md) · [Deploy](docs/DEPLOY.md) · [Admin](docs/ADMIN.md) ·
[Multi-tenant](docs/MULTI_TENANT.md) · [Supabase](docs/SUPABASE.md) ·
[Twenty](docs/TWENTY.md) · [Integrações](docs/INTEGRATIONS.md) ·
[Follow-up](docs/FOLLOWUP.md) · [Playbook](docs/PLAYBOOK.md) ·
[Elite](docs/ELITE.md) · [Arquitetura](docs/ARCHITECTURE.md)

## Roadmap

- [x] MVP: agentes + WhatsApp + Supabase multi-tenant + follow-up + Twenty
- [x] Painel admin (métricas, leads, criação de workspace)
- [x] Idempotência + segurança do webhook
- [x] Logging estruturado (JSON)
- [x] Testes + CI
- [x] Dockerfile + deploy documentado
- [x] Camada de integrações Fase 0+1 (Composio session/authorize/API)
- [x] Playbook por workspace (ICP, pricing, cases, tom → system prompt)
- [x] Módulos elite: score, intent, enrichment, closer tools + API
- [x] Dashboard cliente Next.js (`dashboard/`)
- [ ] Billing por plano (Asaas/Stripe)
- [ ] Testes E2E com mensagem real

## Licença

[MIT](LICENSE).

---
ForceIA — a força de vendas que nunca dorme.
