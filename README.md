# ForceIA

![CI](https://github.com/jvrm831720/forceia/actions/workflows/ci.yml/badge.svg)

**ForceIA** — time de vendas com IA que trabalha 24h.

Agentes SDR + Closer + Follow-up + Relatórios no WhatsApp.

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
| **Install Command** | `npm install` |
| **Build Command** | `npm run build` |
| **Output Directory** | *(vazio — gerenciado pelo Next.js)* |
| **Node.js Version** | 24.x |

```bash
cd dashboard
npm install
npm run build   # deve finalizar com sucesso
npm run dev
```

**Importante:** não use a raiz do repositório como Root Directory. Não há `package.json` de frontend na raiz (monorepo Python + `dashboard/` + `web/`). Deploys com Root Directory `/` falham em 1–2 segundos.

Detalhes: [dashboard/README.md](dashboard/README.md).

## Deploy 24/7
