# ForceIA

**Seu time de vendas de IA que trabalha 24h por menos de 30% do custo de um SDR humano.**

ForceIA e um time completo de agentes de inteligencia artificial especializados em vendas. Eles qualificam leads, agendam reunioes, tiram objecoes e fazem follow-up automaticamente no WhatsApp.

## Arquitetura do MVP

```
ForceIA
├── agents/              # Logica dos agentes (SDR, Closer, Follow-up, Relatorios)
├── channels/            # Integracao WhatsApp (Evolution API)
├── crm/                 # Backend CRM (Twenty)
├── integrations/        # Composio + ferramentas externas
├── config/              # Configuracoes e prompts
├── docker-compose.yml   # Orquestracao local
└── docs/                # Documentacao
```

### Stack open-source

| Camada | Projeto | Uso |
|--------|---------|-----|
| Agente de vendas | [SalesGPT](https://github.com/filip-michalsky/SalesGPT) | Conversa context-aware (estagios de venda) |
| Template SDR | [b2b-sdr-agent-template](https://github.com/iPythoning/b2b-sdr-agent-template) | Pipeline completo + multi-canal |
| Orquestracao multi-agente | CrewAI / LangGraph | Time SDR + Closer + Follow-up |
| WhatsApp | [Evolution API](https://github.com/EvolutionAPI/evolution-api) | Canal principal (Brasil) |
| CRM | [Twenty](https://github.com/twentyhq/twenty) | Pipeline e painel do cliente |
| Integracoes | [Composio](https://github.com/ComposioHQ/composio) | Calendar, Gmail, CRM, etc. |

## Agentes do Time

| Agente | Funcao |
|--------|--------|
| **SDR** | Qualifica leads (BANT) e agenda reunioes |
| **Closer** | Continua a conversa, tira objecoes e avanca o fechamento |
| **Follow-up** | Reativa leads frios e recupera oportunidades |
| **Relatorios** | Envia resumo diario de performance e pipeline |

## Quick Start (MVP local)

### Pre-requisitos
- Docker + Docker Compose
- Node.js 20+
- Python 3.11+
- Chave OpenAI (ou outro LLM)

### 1. Clone e configure

```bash
git clone https://github.com/jvrm831720/forceia.git
cd forceia
cp .env.example .env
# Edite .env com suas chaves
```

### 2. Subir infraestrutura

```bash
docker compose up -d
```

Isso sobe:
- Evolution API (WhatsApp) na porta 8080
- Twenty CRM (quando configurado)
- Redis + Postgres

### 3. Configurar WhatsApp (Evolution API)

1. Acesse http://localhost:8080
2. Crie uma instancia
3. Escaneie o QR Code com o WhatsApp Business
4. Copie o `instanceName` e a API key para o `.env`

### 4. Rodar o agente SDR (MVP)

```bash
cd agents
pip install -r requirements.txt
python run_sdr.py
```

## Precos sugeridos (produto)

| Plano | Preco Mensal |
|-------|--------------|
| Starter | R$ 3.497 |
| Completo | R$ 4.497 |
| Enterprise | a partir de R$ 5.997 |

Setup: R$ 5.900

## Roadmap do MVP

- [x] Scaffold do repositorio
- [ ] Integracao Evolution API (envio/recebimento WhatsApp)
- [ ] Agente SDR basico (qualificacao + agenda)
- [ ] Memoria de conversa
- [ ] Webhook de mensagens -> agente
- [ ] Painel simples de leads
- [ ] Agente Follow-up
- [ ] Relatorio diario
- [ ] Integracao Twenty CRM

## Licenca

MIT (respeitando as licencas dos projetos base).

---

ForceIA - A forca de vendas que nunca dorme.
