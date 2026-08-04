# ForceIA — Codebase Map

> **Mapa vivo do repositório.** Atualize este arquivo a cada marco relevante.
> Última revisão: **2026-08-04** · HEAD aproximado: `479fd0c` · Versão produto: **2.0.0+**

Objetivo do produto: cada empresa-cliente deve sentir que tem o **melhor SDR**, o **melhor Closer** e o **melhor Follow-up** para cada lead — especialistas no vertical dela, não prompts genéricos.

---

## 1. Visão geral

| Item | Valor |
|------|--------|
| Repo | https://github.com/jvrm831720/forceia |
| Produto | Time de vendas de IA multi-tenant (WhatsApp) |
| Agentes | SDR → Closer → Follow-up (LangGraph + OpenAI) |
| Canal | Evolution API (WhatsApp) |
| Dados | Supabase (Postgres multi-tenant) |
| CRM | Twenty (opcional, por workspace) |
| Integrações | Composio (Calendar, LinkedIn, Gmail, Slack…) |
| Painel | FastAPI admin (`:8100`) + console React (`web/`) |
| Runtime | Python 3.11+ |

### Fluxo de uma mensagem

```
WhatsApp (Evolution)
    → webhook_server.py  (multi-tenant por instance)
    → run_sdr / LangGraph graph.py
         prepare  → (enrichment previsto)
         generate → system prompt + playbook + histórico
         parse    → META JSON (BANT, intent, score, schedule…)
         route    → state_machine (stage)
         persist  → messages + leads + events + WhatsApp reply
    → Twenty sync (job opcional)
    → Follow-up job (stale leads)
```

---

## 2. Árvore do repositório

```
forceia/
├── CODEBASE.md              ← este mapa
├── README.md
├── CHANGELOG.md
├── LICENSE                  MIT
├── Dockerfile
├── docker-compose.yml       Evolution + app (webhook + admin)
├── Makefile
├── pyproject.toml
├── .env.example
├── .github/workflows/       CI (ruff + pytest 3.11/3.12)
│
├── agents/                  ★ núcleo Python
│   ├── admin_server.py      Painel FastAPI :8100
│   ├── webhook_server.py    Webhook Evolution :8000
│   ├── run_sdr.py           Runtime diálogo / entry local
│   ├── graph.py             LangGraph (prepare→generate→parse→route→persist)
│   ├── intelligence.py      build_system_prompt + parse META
│   ├── state_machine.py     Transições de stage
│   ├── db.py                Acesso Supabase
│   ├── auth.py              JWT admin
│   ├── whatsapp.py          Envio Evolution
│   ├── twenty_client.py     CRM Twenty
│   ├── workspace_context.py Contexto multi-tenant
│   ├── prompts.py           Carrega prompts editáveis
│   ├── playbook.py          ★ P1 — especialização por workspace
│   ├── playbook_routes.py   API playbook
│   ├── lead_score.py        ★ P2 — score 0–100 + hot leads
│   ├── intent.py            ★ P2 — ready_to_buy vs researching
│   ├── enrichment.py        ★ P2 — enrich pré-mensagem
│   ├── closer_tools.py      ★ P2 — Calendar + proposta/pagamento
│   ├── elite_routes.py      ★ P2 — API hot-leads/enrich/schedule/proposal
│   ├── learning.py          Loop STaR / aprendizado
│   ├── observability.py     Métricas / tracing
│   ├── followup_job.py      Job follow-up
│   ├── sync_twenty_job.py   Job sync CRM
│   ├── scheduler.py         Scheduler em processo
│   ├── create_workspace.py  CLI criar workspace
│   ├── validate_mvp.py      Smoke test
│   ├── improve_agents.py    Utilitário de melhoria de prompts
│   ├── integrations/        Camada Composio
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── composio_client.py
│   │   └── admin_routes.py  Mount integrations + playbook + elite
│   ├── static/              Dashboard HTML legado do admin
│   └── tests/               pytest unitário
│
├── web/                     Console React (Vite)
│   └── src/
│       ├── App.tsx          Overview, leads, transcript, notes, pause
│       ├── PlaybookPanel.tsx Editor de playbook (ICP, pricing…)
│       ├── main.tsx
│       ├── index.css
│       └── playbook.css
│
├── config/prompts/          Prompts base editáveis (sdr/closer/followup)
├── supabase/
│   ├── schema.sql           Schema canônico multi-tenant + playbook
│   ├── playbook.sql         Migration playbook
│   ├── integrations.sql     Migration integrações
│   ├── learning.sql         Migration learning
│   └── migrate_multitenant.sql
├── docker/                  Init Postgres Evolution
└── docs/                    Documentação temática
    ├── SETUP.md
    ├── ARCHITECTURE.md
    ├── ADMIN.md
    ├── MULTI_TENANT.md
    ├── SUPABASE.md
    ├── TWENTY.md
    ├── FOLLOWUP.md
    ├── LEARNING.md
    ├── OBSERVABILITY.md
    ├── INTEGRATIONS.md      Composio Fase 0+1
    ├── PLAYBOOK.md          Prioridade 1
    └── ELITE.md             Prioridade 2
```

---

## 3. Linha do tempo (o que já foi feito)

### Fundação (MVP → ~1.7)

| Capacidade | Onde |
|------------|------|
| Multi-tenant por workspace | `workspaces`, `db.py`, `workspace_context.py` |
| Webhook Evolution multi-instance | `webhook_server.py` |
| Agentes SDR / Closer / Follow-up | `graph.py`, `intelligence.py`, `prompts.py` |
| Máquina de estados (stage) | `state_machine.py` — sdr → qualified → closer → followup → won/lost |
| BANT em JSONB no lead | `leads.bant` + META no parse |
| Histórico de mensagens | `messages` |
| Eventos / auditoria | `events` |
| Follow-up job (stale) | `followup_job.py`, `scheduler.py` |
| Sync Twenty CRM | `twenty_client.py`, `sync_twenty_job.py` |
| Logging estruturado | `logging_config.py`, `observability.py` |
| Docker + compose | `Dockerfile`, `docker-compose.yml` |
| CI ruff + pytest | `.github/workflows` |
| Auth JWT no admin | `auth.py` (v1.6) |
| Tela de lead + transcript | Admin API + `web` (v1.7) |

### v1.8.0 — Operação humana

| Capacidade | Onde |
|------------|------|
| Notas internas no lead | `POST .../leads/{id}/notes`, UI no detalhe |
| Timeline de eventos | `GET .../leads/{id}/events` |
| Assumir conversa / pausar agente | `POST .../leads/{id}/pause` → `metadata.agent_paused` |
| Runtime respeita pause | `run_sdr`, graph, follow-up **não** respondem |

### v1.9.0 — Integrações (Composio)

| Capacidade | Onde |
|------------|------|
| Provider Composio (session, authorize, execute) | `agents/integrations/composio_client.py` |
| Registry + allowlist toolkits | `registry.py`, env `FORCEIA_COMPOSIO_TOOLKITS` |
| API connect/disconnect/health | `integrations/admin_routes.py` |
| Session por workspace | `metadata.composio_session_id` |

### v2.0.0 — Prioridade 1: Playbook (especialização)

| Capacidade | Onde |
|------------|------|
| Schema playbook estruturado | `agents/playbook.py` |
| Coluna `workspaces.playbook` | `supabase/schema.sql`, `playbook.sql` |
| Injeção no system prompt | `intelligence.build_system_prompt` |
| Completeness 0–100 (ready ≥ 50) | `playbook_completeness()` |
| API GET/PUT/template | `playbook_routes.py` |
| Aba Playbook no console | `web/src/PlaybookPanel.tsx` + `App.tsx` |
| Docs | `docs/PLAYBOOK.md` |
| Testes | `agents/tests/test_playbook.py` |

**Campos do playbook:** ICP, persona, pricing, cases, objections, tone, FAQ, script, value props, concorrentes, etc.

### Prioridade 2 — Inteligência de elite (módulos commitados)

| # | Capacidade | Módulo | Status no runtime |
|---|------------|--------|-------------------|
| 5 | Enrichment antes da 1ª msg (heurística + LinkedIn Composio + webhook) | `enrichment.py` | API ✅ · wire no `prepare` ⏳ |
| 6 | Score tempo real + ranking hot leads | `lead_score.py` | API ✅ · wire no `parse` ⏳ |
| 7 | Closer: Calendar real + proposta/link pagamento | `closer_tools.py` | API ✅ · wire no `persist` ⏳ |
| 8 | Detecção ready_to_buy vs researching | `intent.py` | API ✅ · wire no `parse` ⏳ |

Rotas elite (`elite_routes.py`, montadas em `admin_routes`):

- `GET  /api/workspaces/{slug}/hot-leads`
- `GET  /api/workspaces/{slug}/leads/{id}/score`
- `POST /api/workspaces/{slug}/leads/{id}/enrich`
- `POST /api/workspaces/{slug}/leads/{id}/schedule`
- `POST /api/workspaces/{slug}/leads/{id}/proposal`

Docs: `docs/ELITE.md`.

> **Pendente explícito:** encaixar enrich/intent/score/schedule/proposal nos nós do LangGraph (`graph.py` + `intelligence.py`) para rodar automaticamente a cada mensagem WhatsApp (não só via API admin).

---

## 4. Modelo de dados (Supabase)

### `workspaces`
- Isolamento multi-tenant (slug, api_key)
- Credenciais por cliente: Evolution, Twenty, OpenAI opcional
- `plan`, `active`, `followup_*`
- `metadata` JSONB (composio_session, flags…)
- **`playbook` JSONB** — especialização dos agentes

### `leads`
- Unique `(workspace_id, phone)`
- `stage`: sdr | qualified | closer | followup | won | lost
- `bant` JSONB
- `metadata` JSONB — enrichment, score, buying_intent, agent_paused, notes, schedule…

### `messages`
- role: user | assistant | system · `agent` (sdr/closer/followup)

### `events`
- Auditoria: stage_change, internal_note, agent_paused, enrichment, schedule, etc.

Migrations extras: `playbook.sql`, `integrations.sql`, `learning.sql`, `migrate_multitenant.sql`.

---

## 5. APIs admin (resumo)

Auth: `Authorization: Bearer <JWT ou ADMIN_TOKEN>`.

| Área | Endpoints principais |
|------|----------------------|
| Auth | login JWT |
| Workspaces | list/create, KPIs, funil |
| Leads | list, detail+transcript, PATCH stage |
| Notes / events / pause | v1.8 |
| Playbook | GET/PUT/template |
| Integrations | list, connect, disconnect, health |
| Elite | hot-leads, score, enrich, schedule, proposal |

Servidor: `python agents/admin_server.py` → `:8100`.

---

## 6. Console web (`web/`)

- **Overview** — KPIs e funil
- **Leads** — lista com filtros, badge humano/pausado, score futuro
- **Detalhe** — transcript com cores por agente, BANT, notes, timeline, assumir/retomar, troca de stage
- **Playbook** — editor completo + score de prontidão

Stack: React + Vite. Build estático pode ser servido pelo admin ou host separado.

---

## 7. Agentes e prompts

| Agente | Função | Entrada de inteligência |
|--------|--------|-------------------------|
| **SDR** | Qualificar (BANT), rapport, avançar | Playbook + enrichment + intent |
| **Closer** | Fechar, agenda, proposta | Playbook pricing + Calendar + payment link |
| **Follow-up** | Reativar stale sem spam | Playbook tom + regras de intervalo |

Protocolo **META** (JSON no final da resposta do modelo): BANT, stage sugerido, intent, score hints, `schedule`, `send_proposal`.

Prompts base em `config/prompts/`; personalização forte via **playbook** injetado em runtime.

---

## 8. Score de lead (composição)

```
Score 0–100 =
  BANT          até 40
  Intent        até 25   (ready_to_buy no topo)
  Enrichment    até 15
  Engagement    até 10
  Stage         até 10
```

**Hot lead:** score ≥ 70 **ou** `buying_intent = ready_to_buy`.

Intent classes: `ready_to_buy` | `evaluating` | `researching` | `objection` | `nurture`.

---

## 9. Variáveis de ambiente críticas

| Variável | Uso |
|----------|-----|
| `SUPABASE_URL` / `SUPABASE_KEY` | Banco |
| `OPENAI_API_KEY` | LLM (fallback global) |
| `ADMIN_TOKEN` / JWT secrets | Admin |
| `COMPOSIO_API_KEY` | LinkedIn + Calendar |
| `FORCEIA_COMPOSIO` | on/off integrações |
| `FORCEIA_COMPOSIO_TOOLKITS` | Allowlist |
| `FORCEIA_ENRICHMENT_URL` | Webhook enrichment opcional |
| `FORCEIA_PAYMENT_BASE_URL` | Links de proposta/pagamento |
| `FORCEIA_MEETING_DURATION_MIN` | Default 30 |
| Evolution / Twenty | Por workspace no DB ou env |

Ver `.env.example`.

---

## 10. Testes

```
agents/tests/
  test_auth.py
  test_graph_transitions.py
  test_integrations.py
  test_intelligence.py
  test_learning.py
  test_observability.py
  test_playbook.py
  test_state_machine.py
  test_utils.py
```

Rodar: `make test` ou `pytest` (sem dependência de Supabase/OpenAI nos unitários).

Pendente: `test_elite.py` (score/intent/enrich) ainda não versionado no remote.

---

## 11. Roadmap (estado real)

### Feito
- [x] MVP multi-tenant + WhatsApp + BANT + stages
- [x] Admin + JWT + leads + transcript
- [x] Notes, timeline, human takeover (pause)
- [x] Composio session/authorize/API (Fase 0+1)
- [x] Playbook por workspace → system prompt (P1)
- [x] Módulos elite: score, intent, enrichment, closer tools + rotas (P2 backend)

### Em aberto (próximos)
- [ ] **Wire LangGraph** enrich → intent/score → calendar/proposal no fluxo automático
- [ ] UI hot-leads + badges de score/intent no console
- [ ] Billing (Asaas/Stripe) por plano
- [ ] Testes E2E com mensagem real WhatsApp
- [ ] test_elite.py no CI

---

## 12. Como manter este mapa

1. A cada feature grande, atualize a **seção 3 (linha do tempo)** e a **árvore** se novos arquivos.
2. Marque status ✅ / ⏳ na tabela da Prioridade 2 (e futuras).
3. Atualize a data no topo e o SHA aproximado do HEAD.
4. Não substitua o `CHANGELOG.md` — este arquivo é o **mapa estrutural**; o changelog é o histórico versionado.

---

*ForceIA — a força de vendas que nunca dorme.*
