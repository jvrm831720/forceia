# ForceIA — Codebase Map

> **Mapa vivo do repositório.** Atualize este arquivo a cada marco relevante.
> Última revisão: **2026-08-04** · Versão produto: **2.1.0 (P3)**

Objetivo: cada empresa sente que tem o **melhor SDR**, **melhor Closer** e **melhor Follow-up** por lead.

---

## 1. Visão geral

| Item | Valor |
|------|--------|
| Repo | https://github.com/jvrm831720/forceia |
| Agentes | SDR → Closer → Follow-up (LangGraph + OpenAI) |
| Canal | Evolution API (WhatsApp) |
| Dados | Supabase multi-tenant |
| CRM | Twenty (opcional) |
| Integrações | Composio |
| Painel | FastAPI `:8100` + React `web/` |

---

## 2. Árvore (destaques P1–P3)

```
agents/
  playbook.py, playbook_routes.py          # P1
  lead_score.py, intent.py, enrichment.py,
  closer_tools.py, elite_routes.py         # P2
  performance.py                           # P3 KPIs + headline
  owner_reports.py                         # P3 relatório WhatsApp dono
  playground.py                            # P3 simulação
  product_routes.py                        # P3 API
  integrations/admin_routes.py             # mount P1+P2+P3
web/src/
  App.tsx                  # Time · Performance · Playground · Leads…
  PerformancePanel.tsx
  PlaygroundPanel.tsx
  PlaybookPanel.tsx
  product.css
docs/
  PLAYBOOK.md · ELITE.md · PRODUCT.md
```

---

## 3. Linha do tempo

### Fundação → 1.9
MVP, multi-tenant, WhatsApp, BANT, stages, admin JWT, notes/timeline/pause, Composio.

### P1 — Playbook (2.0)
ICP/pricing/cases/tom por workspace no system prompt + aba Playbook.

### P2 — Elite
API: enrichment, score/hot-leads, intent, calendar/proposal. Wire LangGraph ⏳.

### **P3 — Experiência de produto ✅**

| # | Feature | Onde |
|---|---------|------|
| 9 | Dashboard “SDR agendou X reuniões” + IA vs humano | `performance.py` + aba Performance |
| 10 | Relatório WhatsApp para o dono | `owner_reports.py` |
| 11 | Playground lead fictício | `playground.py` + aba Playground |
| 12 | UI premium (painel de time) | App copy + `product.css` |

**APIs P3**
- `GET /api/workspaces/{slug}/performance?period=week|day|month`
- `GET /api/workspaces/{slug}/reports/preview`
- `POST /api/workspaces/{slug}/reports/send`
- `PUT /api/workspaces/{slug}/owner-phone`
- `POST /api/workspaces/{slug}/playground`

---

## 4. Dados

Sem migration nova na P3. Usa `events` + `metadata.owner_phone`. Playground não grava leads.

---

## 5. Roadmap

**Feito:** MVP, pause, Composio, Playbook, Elite API, Product UX (P3).

**Aberto:** wire LangGraph P2 · hot-leads UI · cron relatório dono · billing · E2E.

---

*ForceIA — a força de vendas que nunca dorme.*
