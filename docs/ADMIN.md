# Painel Admin - ForceIA

Console interno para acompanhar workspaces, pipeline, leads e eventos, e para
criar novos clientes sem SQL.

## Ligar o painel

1. Defina um token forte no `.env`:

   ```env
   ADMIN_TOKEN=$(openssl rand -hex 24)
   ```

   Sem `ADMIN_TOKEN`, as rotas de dados retornam **503** (desligado por seguranca).

2. Suba o servidor:

   ```bash
   cd agents
   python admin_server.py          # http://localhost:8100
   # ou: make admin
   ```

3. Abra `http://localhost:8100`, cole o `ADMIN_TOKEN` e entre.

## O que da pra fazer

- Ver **KPIs**: leads totais, taxa de fechamento, leads em negociacao
- Ver o **pipeline** (funil por estagio) de cada workspace
- Listar **leads recentes** com estagio e ultima mensagem
- Acompanhar a **atividade** (eventos) em tempo nao-real (atualizacao manual)
- **Criar workspace** e receber o `api_key` na hora

## API (para automacoes)

Todas as rotas de dados exigem o header `X-Admin-Token: <ADMIN_TOKEN>`
(ou `Authorization: Bearer <ADMIN_TOKEN>`).

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/api/workspaces` | Lista workspaces ativos |
| POST | `/api/workspaces` | Cria workspace `{name, slug, instance?, plan?}` |
| GET | `/api/workspaces/{slug}/metrics` | Totais + contagem por estagio + win rate |
| GET | `/api/workspaces/{slug}/leads?limit=100` | Leads recentes |
| GET | `/api/workspaces/{slug}/events?limit=50` | Eventos recentes |
| GET | `/health` | Status (nao exige token) |

Exemplo:

```bash
curl -H "X-Admin-Token: $ADMIN_TOKEN" \
  http://localhost:8100/api/workspaces/default/metrics
```

## Seguranca

- O painel e **somente leitura** + criacao de workspace. Nao expoe chaves de
  clientes existentes nas listagens.
- Rode atras de HTTPS e, de preferencia, restrito por IP/VPN.
- O token e comparado com `secrets.compare_digest` (resistente a timing attack).
