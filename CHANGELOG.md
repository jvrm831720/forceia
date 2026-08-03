# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [1.5.0]

### Adicionado
- **Langfuse** observabilidade (`agents/observability.py`):
  - Trace `forceia.turn` por mensagem (session = workspace:phone)
  - Spans prepare/generate/parse/route/persist + generation OpenAI
  - Eventos meta_extracted, transition, turn_error
  - Docs `docs/OBSERVABILITY.md`

## [1.4.0]

### Adicionado
- **LangGraph** como orquestrador do funil (`agents/graph.py`):
  - StateGraph: prepare → generate (retry) → parse → route → persist
  - Checkpoints por lead (`thread_id = workspace:phone`), MemorySaver ou SQLite
  - `FORCEIA_USE_GRAPH=1` (padrao) com fallback automatico para fluxo legado
- Dependencias: `langgraph`, `langchain-core`

### Alterado
- `run_sdr.handle_incoming` delega ao grafo quando disponivel
- `state_machine.py` permanece como regras de transicao (fonte unica)

## [1.3.0]

### Adicionado
- **STaR + SPIN no ciclo de learning** (prompt-level, sem fine-tune de pesos):
  - SPIN: pares preferência `real`(won) vs `generated`(lost) + discriminator
  - STaR: racionalização de lost (counterfactual + filtro de qualidade)
  - Modos CLI: `--mode hybrid|spin|star|classic`
  - `--export-prefs PATH` exporta dataset no schema SPIN/HF
- Testes de pares SPIN e export (`test_learning.py`).

## [1.2.0]

### Adicionado
- **Auto-melhoria assistida** (`learning.py`, `improve_agents.py`):
  analisa leads won/lost, gera `prompt_suggestions` e só entra em produção
  após aprovação humana (`--approve` / `--apply` ou API admin).
- Tabelas `learning_runs`, `prompt_suggestions`, `agent_prompt_overrides`
  (`supabase/learning.sql`).
- Overrides de prompt por workspace no `load_prompt`.
- Endpoints admin `/api/learning/*`.
- Docs `docs/LEARNING.md` e testes `test_learning.py`.

## [1.1.0]

### Adicionado
- Camada `intelligence.py`: BANT persistente, score 0-100, bloco `---META---`,
  extracao de nome/empresa/email, contexto vivo no system prompt.
- Prompts de SDR/Closer/Follow-up reescritos (playbook WhatsApp B2B BR).
- Auto-qualificacao quando BANT atinge score minimo.
- Handoff humano via `handoff: true` no META.
- Testes de inteligencia (`test_intelligence.py`).

### Alterado
- `run_sdr.py` injeta memoria do lead e temperatura por agente.
- Follow-up job usa historico + BANT para personalizar mensagem.
- Tags legadas ainda funcionam; META e o protocolo preferencial.

## [1.0.0]

### Adicionado
- **Painel admin** (`admin_server.py` + `static/admin.html`).
- Webhook com idempotencia e token opcional.
- Logging estruturado, testes, CI, Docker, Makefile.
