# ForceIA - imagem da aplicacao (webhook / admin / jobs)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias primeiro (cache de build)
COPY agents/requirements.txt ./agents/requirements.txt
RUN pip install --no-cache-dir -r agents/requirements.txt

# Codigo
COPY agents ./agents
COPY config ./config
COPY .env.example ./.env.example

WORKDIR /app/agents

# Usuario nao-root
RUN useradd -m forceia && chown -R forceia:forceia /app
USER forceia

EXPOSE 8000 8100

# Por padrao sobe o webhook; sobrescreva 'command' no compose para admin/jobs
CMD ["python", "-m", "uvicorn", "webhook_server:app", "--host", "0.0.0.0", "--port", "8000"]
