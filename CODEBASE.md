# ForceIA — Codebase Map

> Última revisão: **2026-08-04** · Versão: **2.4.0 (P0 LangGraph wire)**

Objetivo: melhor SDR / Closer / Follow-up **por lead**, com playbook, inteligência, produto, confiança e **skills de prospecting de elite**.

---

## Prioridades

| P | Tema | Status |
|---|------|--------|
| 1 | Playbook | ✅ |
| 2 | Elite (score/intent/enrich/calendar) | ✅ **wired no LangGraph (P0)** |
| 3 | Product UX | ✅ |
| 4 | Trust (guardrails, A/B, handoff) | ✅ **wired no LangGraph (P0)** |
| **Skills** | ICP fit, personalization, pre-call, revival, pipeline | ✅ |

### P0 — LangGraph (2026-08-04)

No `agents/graph.py`, cada turno agora:

1. **prepare** — enrichment (`enrich_lead`), variante A/B, intent lexical, `compute_lead_score`
2. **generate** — prompt A/B (`resolve_prompt_for_variant`) + `record_ab_exposure`
3. **parse** — `enforce_guardrails`, intent refinado (META+lexical), score no metadata, auto-qualify por BANT/score/intent
4. **actions** — `run_agent_actions` + `execute_closer_actions` (calendar/proposta); flag `wants_meeting` se `ready_to_buy`
5. **persist** — `execute_handoff` completo (pause + notify humano) + persiste score/intent

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

WhatsApp (Evolution) → LangGraph (P0 wired) → playbook + guardrails + **skills** + META → Supabase

Painel: FastAPI `:8100` + React `web/`

---

## Roadmap aberto

- [x] Wire LangGraph completo (P2 elite + guardrails + A/B + handoff)
- UI badges ICP/health no console
- List building em massa (Composio/Twenty)
- Billing · E2E
- Política de turnos por stage (P1)
- Skills condicionais por message_count (P1)

---

*ForceIA — a força de vendas que nunca dorme.*
