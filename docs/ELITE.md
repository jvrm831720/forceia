# Prioridade 2 — Inteligência de elite

## 1. Enrichment (`enrichment.py`)

Antes da primeira resposta (nó `prepare` do LangGraph):

- Heurística na mensagem (nome, empresa, cargo)
- Composio LinkedIn (se conectado)
- Webhook opcional `FORCEIA_ENRICHMENT_URL`

Persiste em `metadata.enrichment` e preenche `name` / `company` / `email` se vazios.

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -d '{"force":true,"text":"Me chamo Ana, da Clínica Sol"}' \
  http://localhost:8100/api/workspaces/demo/leads/{id}/enrich
```

## 2. Score + hot leads (`lead_score.py`)

Score 0–100: BANT (40) + intent (25) + enrichment (15) + engagement (10) + stage (10).

Hot: score ≥ 70 **ou** `buying_intent=ready_to_buy`.

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8100/api/workspaces/demo/hot-leads?limit=20
```

## 3. Closer tools (`closer_tools.py`)

- **Calendar** via Composio (`GOOGLECALENDAR_CREATE_EVENT`) ou link template Google Calendar
- **Proposta / pagamento** via `FORCEIA_PAYMENT_BASE_URL` + playbook pricing

META do closer:

```json
{"schedule":{"start":"2026-08-10T15:00:00-03:00","title":"Demo"},"send_proposal":true,"plan":"pro"}
```

## 4. Intent (`intent.py`)

Classes: `ready_to_buy` | `evaluating` | `researching` | `objection` | `nurture`

Lexical PT-BR + campo `intent` do META. Ready-to-buy em SDR → avança para qualified/closer.

## Env

| Variável | Uso |
|----------|-----|
| `COMPOSIO_API_KEY` | LinkedIn + Calendar |
| `FORCEIA_COMPOSIO` | on/off |
| `FORCEIA_ENRICHMENT_URL` | webhook de enrichment |
| `FORCEIA_PAYMENT_BASE_URL` | link de proposta/pagamento |
| `FORCEIA_MEETING_DURATION_MIN` | default 30 |

## Fluxo no grafo

`prepare` (enrich) → `generate` → `parse` (intent + score) → `route` → `persist` (calendar/proposal + WhatsApp)
