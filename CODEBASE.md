# ForceIA — Codebase Map

> Última revisão: **2026-08-04** · Versão: **2.3.0 (Skills de elite)**

Objetivo: melhor SDR / Closer / Follow-up **por lead**, com playbook, inteligência, produto, confiança e **skills de prospecting de elite**.

---

## Prioridades

| P | Tema | Status |
|---|------|--------|
| 1 | Playbook | ✅ |
| 2 | Elite (score/intent/enrich/calendar) | ✅ API · wire graph ⏳ |
| 3 | Product UX | ✅ |
| 4 | Trust (guardrails, A/B, handoff) | ✅ |
| **Skills** | ICP fit, personalization, pre-call, revival, pipeline | ✅ |

---

## Skills (`agents/skills/`)

Injetadas no **system prompt** via `intelligence.build_system_prompt`:

- `icp_fit` — score 1–100 + grade
- `personalization` — openers SDR
- `pre_call` — brief Closer
- `revival` — reativação lost
- `pipeline_health` — Hot/Warm/Cold/At Risk

API: `GET /api/skills` · `GET /api/workspaces/{slug}/leads/{id}/skills`

Docs: `docs/SKILLS.md`

---

## Stack

WhatsApp (Evolution) → LangGraph/legado → playbook + guardrails + **skills** + META → Supabase

Painel: FastAPI `:8100` + React `web/`

---

## Roadmap aberto

- Wire LangGraph completo (P2 + skills)
- UI badges ICP/health no console
- List building em massa (Composio/Twenty)
- Billing · E2E

---

*ForceIA — a força de vendas que nunca dorme.*
