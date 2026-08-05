# ForceIA — Codebase Map

> Última revisão: **2026-08-04** · Versão: **2.6.0 (P2 console badges · bulk · closer registry)**

Objetivo: melhor SDR / Closer / Follow-up **por lead**, com playbook, inteligência, produto, confiança e **skills de prospecting de elite**.

---

## Prioridades

| P | Tema | Status |
|---|------|--------|
| 1 | Playbook | ✅ |
| 2 | Elite (score/intent/enrich/calendar) | ✅ wired LangGraph (P0) |
| 3 | Product UX | ✅ |
| 4 | Trust (guardrails, A/B, handoff) | ✅ wired LangGraph (P0) |
| **P1** | Turn policy · memória BANT · skills condicionais · intent→rota | ✅ |
| **P2** | Console badges · bulk list building · closer tool registry | ✅ |
| **Skills** | ICP, personalization, pre-call, revival, pipeline | ✅ condicionais |

### P2 — 2026-08-04

- `lead_badges.py` — score / ICP / health / intent por lead (+ agregados de workspace)
- `list_builder.py` — import em massa (normalize phone BR, upsert, optional Twenty)
- `tools/closer_registry.py` — tools formais (`schedule_meeting`, `send_proposal`, `request_handoff`) via META
- `p2_routes.py` — `/leads-enriched`, `/metrics-intel`, `/leads/bulk`, `/tools/closer`, execute tool
- Admin console — colunas de badges + chips intel + UI de bulk import
- Graph overlay — `_node_actions` prefere `closer_registry` (fallback P0)

### P1 — 2026-08-04

- `turn_policy.py` — objetivos por stage, max 1 `?`, trim WhatsApp, objection streak
- `intelligence.build_lead_context` — “já sabemos / ainda falta” (anti-repetição)
- Skills condicionais por `message_count` / stage / tier
- Intent guia agente e stage no LangGraph

### P0 — LangGraph wire

prepare → enrichment, A/B, intent, score · generate → A/B prompt · parse → guardrails · actions → closer_tools · persist → execute_handoff

---

## Skills (`agents/skills/`)

Injetadas sob condição (P1):

- `icp_fit` — early ou tier ≠ hot
- `hiring_signal` / `personalization` — abertura SDR
- `pre_call` — closer / qualified
- `revival` — followup / lost
- `pipeline_health` — se não hot ou conversa longa

---

## Stack

WhatsApp (Evolution) → LangGraph (P0+P1+P2) → playbook + guardrails + turn policy + skills + META tools → Supabase / Twenty

---

## Roadmap aberto

- [x] Wire LangGraph P0
- [x] P1 turn policy / intent routing / skills condicionais
- [x] UI badges ICP/health no console
- [x] List building em massa
- [x] Tools formais no closer (registry + META)
- Billing · E2E
- bind_tools nativo (OpenAI tools) opcional

---

*ForceIA — a força de vendas que nunca dorme.*
