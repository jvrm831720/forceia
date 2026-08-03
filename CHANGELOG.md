# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

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
- **Painel admin** (`admin_server.py` + `static/admin.html`): KPIs, funil de
  pipeline, leads, eventos e criacao de workspace, protegido por `ADMIN_TOKEN`.
- **Idempotencia de webhook**: mensagens repetidas (mesmo `message_id`) sao
  ignoradas.
- **Seguranca do webhook**: token compartilhado opcional (`WEBHOOK_SHARED_TOKEN`)
  e guarda de fallback para workspace default (`WEBHOOK_ALLOW_DEFAULT_FALLBACK`).
- **Logging estruturado** (`logging_config.py`): texto ou JSON (`LOG_FORMAT=json`).
- **Modulos puros e testaveis**: `utils.py` e `whatsapp.py`.
- **Suite de testes** (`agents/tests/`) com pytest, sem dependencia de servicos
  externos (19 testes).
- **CI** (GitHub Actions): ruff + pytest em Python 3.11 e 3.12.
- **Deploy**: `Dockerfile`, `.dockerignore`, servicos `forceia-webhook` e
  `forceia-admin` no compose (profile `app`) e `docs/DEPLOY.md`.
- Ferramentas de projeto: `pyproject.toml` (ruff + pytest), `Makefile`,
  `.gitignore`, `LICENSE` (MIT), `CONTRIBUTING.md`, `docs/ADMIN.md`.

### Corrigido
- Tags de controle (`[QUALIFICADO]`, `[FECHADO]`, etc.) agora sao removidas da
  resposta antes de enviar ao lead (o cliente nao ve mais as tags).
- `generate_reply` valida a ausencia de `OPENAI_API_KEY` com erro claro.

### Alterado
- `requirements.txt` limpo: removidas dependencias nao usadas (`langchain`,
  `langchain-openai`, `langgraph`). Novo `requirements-dev.txt`.
- Cliente OpenAI passa a ser cacheado por chave (menos overhead por mensagem).
- `normalize_phone` centralizado em `utils.py` (reaproveitado pelo Twenty).
- `validate_mvp.py` cobre os novos modulos e funcoes.
