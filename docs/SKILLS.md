# Skills de elite — ForceIA

Inspiradas em playbooks de prospecting de alto nível, **adaptadas ao stack ForceIA** — sem Amplemarket MCP.

## Catálogo

| ID | Skill | Onde age |
|----|-------|----------|
| `enrich_and_score` | ICP Fit Score 1–100 | Todos |
| `outreach_personalization` | Openers WhatsApp | SDR |
| `pre_call_brief` | Talking points / landmines | Closer |
| `closed_lost_revival` | Reativação lost | Follow-up |
| `pipeline_health` | Hot/Warm/Cold/At Risk | Todos |
| **`hiring_signal_prospector`** | Vaga → intent + opener | SDR (se `metadata.hiring_signal`) |

## Hiring Signal

Analisa JD / role e classifica **Strong / Medium / Soft**, infere dor, conecta ao playbook e gera opener.

```bash
# Analisar vaga (opcional attach no lead)
POST /api/workspaces/{slug}/skills/hiring-signal
{
  "role": "SDR (First Hire)",
  "company": "CloudMetrics",
  "jd_snippet": "We're looking for our first SDR to build outbound from the ground up.",
  "decision_maker_name": "Alex",
  "lead_id": "uuid-opcional",
  "attach_to_lead": true
}
```

Com `attach_to_lead`, grava `metadata.hiring_signal` e o **system prompt do SDR** usa o opener automaticamente.

## API geral

```bash
GET /api/skills
GET /api/workspaces/{slug}/leads/{id}/skills
```

## Módulos

```
agents/skills/
  icp_fit.py · personalization.py · pre_call.py
  revival.py · pipeline_health.py · hiring_signal.py
```
