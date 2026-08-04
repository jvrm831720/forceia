# ForceIA — Codebase Map

> **Mapa vivo do repositório.** Última revisão: **2026-08-04** · Versão: **2.2.0 (P4)**

Objetivo: cada empresa sente que tem o **melhor SDR**, **melhor Closer** e **melhor Follow-up** por lead — com **confiança** (não inventa preço/prazo).

---

## 1. Visão geral

| Item | Valor |
|------|--------|
| Repo | https://github.com/jvrm831720/forceia |
| Agentes | SDR → Closer → Follow-up |
| Canal | Evolution API |
| Dados | Supabase multi-tenant |
| Painel | FastAPI + React |

---

## 2. Árvore (P1–P4)

```
agents/
  playbook.py                         # P1
  lead_score, intent, enrichment,
  closer_tools, elite_routes          # P2
  performance, owner_reports,
  playground, product_routes          # P3
  guardrails.py                       # P4 — preço/prazo
  ab_testing.py                       # P4 — A/B conversão
  handoff.py                          # P4 — resumo + notify
  trust_routes.py                     # P4 API
  intelligence.py                     # + guardrails no prompt
  run_sdr.py                          # + guardrails, A/B, handoff
docs/
  PLAYBOOK · ELITE · PRODUCT · TRUST.md
```

---

## 3. Linha do tempo

| Prioridade | Status |
|------------|--------|
| P1 Playbook | ✅ |
| P2 Elite (API; wire graph ⏳) | ✅ módulos |
| P3 Product UX | ✅ |
| **P4 Confiabilidade** | ✅ |

### P4 — detalhes

| # | Feature | Módulo |
|---|---------|--------|
| 13 | Guardrails (não inventar preço/prazo) | `guardrails.py` |
| 14 | A/B prompts + conversão | `ab_testing.py` |
| 15 | Handoff suave (resumo + WhatsApp) | `handoff.py` |

**APIs P4**
- `GET  /api/workspaces/{slug}/ab-report`
- `POST /api/workspaces/{slug}/leads/{id}/handoff`
- `POST /api/workspaces/{slug}/guardrails/scan`

---

## 4. Runtime (legado)

```
lead → assign A/B → prompt variante → LLM
     → split META → enforce_guardrails
     → se handoff: pause + notify humano
     → persist + WhatsApp
```

---

## 5. Roadmap aberto

- Wire LangGraph P2 no fluxo WhatsApp
- UI hot-leads / A/B no painel
- Cron relatório dono
- Billing · E2E

---

*ForceIA — a força de vendas que nunca dorme.*
