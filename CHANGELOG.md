# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [2.1.0] — Prioridade 3 · Experiência de produto

### Adicionado
- **Dashboard de performance** (`agents/performance.py`)
  - Headline: “Seu SDR de IA agendou X reuniões esta semana”
  - Comparativo IA vs humano (reuniões, qualificações, fechamentos)
  - `GET /api/workspaces/{slug}/performance?period=week|day|month`
- **Relatório WhatsApp para o dono** (`agents/owner_reports.py`)
  - Preview + envio via Evolution
  - `GET .../reports/preview` · `POST .../reports/send`
  - `PUT .../owner-phone` → `metadata.owner_phone`
- **Playground** (`agents/playground.py`)
  - Simula SDR/Closer com lead fictício (não grava no funil)
  - `POST /api/workspaces/{slug}/playground`
- **UI premium**
  - Abas Time · Performance · Playground
  - `PerformancePanel.tsx` · `PlaygroundPanel.tsx` · `product.css`
  - Copy “painel de time de vendas / empresas”
- Docs: `docs/PRODUCT.md` · testes `agents/tests/test_product.py`
- `product_routes.py` montado em `integrations/admin_routes.py`

## [2.0.0]

### Adicionado
- **Playbook por workspace (Prioridade 1)**
  - `agents/playbook.py`, coluna `workspaces.playbook`, API GET/PUT/template
  - Aba Playbook no console + score de completude
  - Docs: `docs/PLAYBOOK.md`

## [1.9.0]

### Adicionado
- Camada de integrações Composio (session, authorize, admin API)

## [1.8.0]

### Adicionado
- Notas internas, timeline de eventos, assumir/pausar agente

## [1.7.x]

### Adicionado
- Tela de lead + transcript e melhorias de UI

## [1.6.0]

### Adicionado
- Auth JWT no painel admin
