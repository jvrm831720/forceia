# Skills de elite — ForceIA

Inspiradas em playbooks de prospecting de alto nível (enrich & score, personalization, pre-call, revival, pipeline health), **adaptadas ao stack ForceIA** — sem depender de Amplemarket MCP.

Usam: **playbook do workspace**, **enrichment**, **BANT**, **intent**, **mensagens**.

## Catálogo

| ID | Skill | Onde age |
|----|-------|----------|
| `enrich_and_score` | ICP Fit Score 1–100 (grade A–F) | Todos os agentes |
| `outreach_personalization` | Ângulos + openers WhatsApp | SDR |
| `pre_call_brief` | Talking points, perguntas, landmines | Closer |
| `closed_lost_revival` | Prioridade + opener de reativação | Follow-up / lost |
| `pipeline_health` | Health 1–10 · Hot/Warm/Cold/At Risk | Todos |

## Injeção automática

`intelligence.build_system_prompt` chama `skills.build_skills_context` e injeta o bloco certo conforme **agent/stage**.

## API

```bash
# Lista skills
GET /api/skills

# Perfil completo de um lead
GET /api/workspaces/{slug}/leads/{id}/skills
```

## Módulos

```
agents/skills/
  __init__.py          # registry + build_skills_context
  icp_fit.py
  personalization.py
  pre_call.py
  revival.py
  pipeline_health.py
agents/skills_routes.py
```

## Mapeamento das skills originais

| Skill Amplemarket (referência) | Implementação ForceIA |
|--------------------------------|------------------------|
| enrich-and-score-lead | `icp_fit` + enrichment existente |
| outreach-personalization-research | `personalization` |
| pre-call-research-brief | `pre_call` |
| closed-lost-revival-scanner | `revival` |
| pipeline-account-review | `pipeline_health` |
| build-targeted-lead-list / icp-refiner | Playbook UI + ICP fields (P1) |
| deal-contact-gap / duo-copilot | Roadmap (CRM Twenty + performance P3) |

Skills que exigem HubSpot/Amplemarket full (list building em massa, Duo Slack) ficam no roadmap com Composio + Twenty.
