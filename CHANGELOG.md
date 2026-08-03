# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

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
  externos.
- **CI** (GitHub Actions): ruff + pytest em Python 3.11 e 3.12.
- **Deploy**: `Dockerfile`, `.dockerignore`, servicos no compose (profile `app`)
  e `docs/DEPLOY.md`.
- Ferramentas de projeto: `pyproject.toml` (ruff + pytest), `Makefile`,
  `.gitignore`, `LICENSE` (MIT), `CONTRIBUTING.md`, `docs/ADMIN.md`.

### Corrigido
- Tags de controle (`[QUALIFICADO]`, `[FECHADO]`, etc.) agora sao removidas da
  resposta antes de enviar ao lead.
- `generate_reply` valida a ausencia de `OPENAI_API_KEY` com erro claro.

### Alterado
- `requirements.txt` limpo: removidas dependencias nao usadas (`langchain`, etc.).
- Cliente OpenAI passa a ser cacheado por chave.
- `normalize_phone` centralizado em `utils.py`.
- `validate_mvp.py` cobre os novos modulos e funcoes.
