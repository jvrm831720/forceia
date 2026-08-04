# ForceIA

**Time de vendas de IA multi-tenant** — WhatsApp + SDR / Closer / Follow-up + Supabase + Twenty.

> A força de vendas que nunca dorme.

![CI](https://github.com/jvrm831720/forceia/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Repo: https://github.com/jvrm831720/forceia

---

## O que é

Agentes de IA (SDR, Closer e Follow-up) atendem leads no WhatsApp, qualificam com
BANT, avançam o funil por uma máquina de estados e sincronizam com o CRM Twenty.
Cada cliente é um **workspace** isolado no Supabase.

## Stack

| Camada | Tecnologia |
|--------|------------|
| WhatsApp | Evolution API |
| Agentes | Python + OpenAI |
| Banco | Supabase (multi-tenant) |
| CRM | Twenty (opcional, por workspace) |
| Jobs | Follow-up + sync Twenty |
| Painel | FastAPI + dashboard HTML |

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

KPIs, funil de pipeline, leads, eventos e criação de workspace. Veja [docs/ADMIN.md](docs/ADMIN.md).

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
pytest              # 19 testes, sem serviços externos
```

CI roda `ruff` + `pytest` em Python 3.11 e 3.12 a cada push/PR.

## Estrutura

```
agents/            agentes, webhook, painel admin, jobs e testes
  static/          dashboard do painel admin
  tests/           testes unitários (pytest)
config/prompts/    prompts editáveis (sdr / closer / followup)
supabase/          schema.sql + migração multi-tenant
docker/            init do Postgres da Evolution
docs/              documentação
```

## Documentação

[Setup](docs/SETUP.md) · [Deploy](docs/DEPLOY.md) · [Admin](docs/ADMIN.md) ·
[Multi-tenant](docs/MULTI_TENANT.md) · [Supabase](docs/SUPABASE.md) ·
[Twenty](docs/TWENTY.md) · [Integrações](docs/INTEGRATIONS.md) · [Follow-up](docs/FOLLOWUP.md) · [Playbook](docs/PLAYBOOK.md) · [Arquitetura](docs/ARCHITECTURE.md)

## Roadmap

- [x] MVP: agentes + WhatsApp + Supabase multi-tenant + follow-up + Twenty
- [x] Painel admin (métricas, leads, criação de workspace)
- [x] Idempotência + segurança do webhook
- [x] Logging estruturado (JSON)
- [x] Testes + CI
- [x] Dockerfile + deploy documentado
- [x] Camada de integrações Fase 0+1 (Composio session/authorize/API) — ver docs/INTEGRATIONS.md
- [x] Playbook por workspace (ICP, pricing, cases, tom → system prompt)
- [ ] Agendamento real (Calendar tool no Closer) e triggers
- [ ] Billing por plano (Asaas/Stripe)
- [ ] Testes E2E com mensagem real

## Licença

[MIT](LICENSE).

---
ForceIA — a força de vendas que nunca dorme.
