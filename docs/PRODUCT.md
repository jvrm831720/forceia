# Prioridade 3 — Experiência de produto

## 9. Dashboard de performance

`GET /api/workspaces/{slug}/performance?period=week|day|month`

Retorna headline do tipo:

> Seu SDR de IA agendou **3** reuniões esta semana

Comparativo **IA vs humano** em reuniões, qualificações e fechamentos.

Fonte: eventos (`meeting_scheduled`, `stage_changed`, `proposal_generated`, `agent_paused`…).

## 10. Relatório WhatsApp para o dono

```bash
# Preview
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8100/api/workspaces/demo/reports/preview?period=week"

# Enviar
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -d '{"period":"week"}' \
  http://localhost:8100/api/workspaces/demo/reports/send

# Configurar telefone do dono
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -d '{"phone":"5511999998888"}' \
  http://localhost:8100/api/workspaces/demo/owner-phone
```

Telefone: `metadata.owner_phone` ou body `phone` ou env `FORCEIA_OWNER_PHONE`.

## 11. Playground

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"Oi, quero saber de preços","lead":{"name":"Ana","company":"Clínica Sol"}}' \
  http://localhost:8100/api/workspaces/demo/playground
```

Não grava lead real. Usa playbook + prompts do workspace. Envie `history` nos turnos seguintes.

## 12. UI premium

Console React com abas **Performance** e **Playground**, headline de time de vendas e comparativo IA/humano no overview.

## Módulos

| Arquivo | Função |
|---------|--------|
| `agents/performance.py` | KPIs + headline |
| `agents/owner_reports.py` | Texto + envio WhatsApp |
| `agents/playground.py` | Simulação in-memory |
| `agents/product_routes.py` | Rotas admin |
