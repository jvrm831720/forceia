# ForceIA — Codebase Map

> Última revisão: **2026-08-04** · Versão: **2.5.0 (P1 turn policy + intent routing)**

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
| **Skills** | ICP, personalization, pre-call, revival, pipeline | ✅ condicionais |

### P1 — 2026-08-04

- `agents/turn_policy.py` — objetivos por stage, max 1 `?`, trim WhatsApp, objection streak
- `intelligence.build_lead_context` — “já sabemos / ainda falta” (anti-repetição)
- `intelligence.build_system_prompt` — bloco de política de turno + intent guidance
- `skills.build_skills_context` — thresholds por `message_count` / stage / tier
- `graph` — intent→agente/stage, `enforce_turn_policy` no parse, handoff por 2+ objeções
- `run_sdr` — passa `agent` + `history` ao system prompt

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

WhatsApp (Evolution) → LangGraph (P0+P1) → playbook + guardrails + turn policy + skills + META → Supabase

---

## Roadmap aberto

- [x] Wire LangGraph P0
- [x] P1 turn policy / intent routing / skills condicionais
- UI badges ICP/health no console
- List building em massa (Composio/Twenty)
- Billing · E2E
- Tools formais no closer (bind_tools)

---

*ForceIA — a força de vendas que nunca dorme.*
