# ForceIA - atalhos de desenvolvimento
.DEFAULT_GOAL := help
PY ?= python3

.PHONY: help install install-dev lint fmt test validate run webhook admin followup \
        compose-up compose-app-up compose-down

help: ## Lista os comandos
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	 awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependencias de runtime
	$(PY) -m pip install -r agents/requirements.txt

install-dev: ## Instala dependencias de desenvolvimento (inclui runtime)
	$(PY) -m pip install -r agents/requirements-dev.txt

lint: ## Roda o ruff
	$(PY) -m ruff check agents

fmt: ## Corrige lint automaticamente
	$(PY) -m ruff check --fix agents

test: ## Roda os testes unitarios
	$(PY) -m pytest

validate: ## Smoke test do MVP (precisa de .env)
	cd agents && $(PY) validate_mvp.py

run: ## Dialogo local com o agente
	cd agents && $(PY) run_sdr.py

webhook: ## Sobe o webhook (porta 8000)
	cd agents && $(PY) -m uvicorn webhook_server:app --host 0.0.0.0 --port 8000 --reload

admin: ## Sobe o painel admin (porta 8100)
	cd agents && $(PY) -m uvicorn admin_server:app --host 0.0.0.0 --port 8100 --reload

followup: ## Roda o job de follow-up (dry-run)
	cd agents && $(PY) followup_job.py --all --dry-run

compose-up: ## Sobe apenas a infra (Evolution + Postgres + Redis)
	docker compose up -d

compose-app-up: ## Sobe infra + app (webhook + admin)
	docker compose --profile app up -d --build

compose-down: ## Derruba tudo
	docker compose --profile app down
