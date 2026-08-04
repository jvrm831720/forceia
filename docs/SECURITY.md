# Segurança — ForceIA

## Achados e mitigações (2026-08-04)

| Risco | Severidade | Mitigação |
|-------|------------|-----------|
| Webhook sem autenticação forte (só instance name) | Alta | `WEBHOOK_SECRET` + `X-Workspace-Key` em prod; rate limit |
| Brute-force login admin | Alta | Rate limit 10/min/IP; política de senha forte |
| JWT_SECRET fraco / default | Alta | ≥32 chars; aviso/erro em produção |
| SSRF no scraper (localhost, metadata AWS) | Alta | `validate_public_http_url` + bloqueio pós-redirect |
| Leak do texto da reply no webhook | Média | Em `FORCEIA_ENV=production` só `{replied: bool}` |
| ADMIN_TOKEN legado eterno | Média | `FORCEIA_DISABLE_LEGACY_TOKEN=1` |
| Headers XSS/clickjacking | Baixa | CSP, X-Frame-Options, nosniff |

## Checklist de produção

```bash
export FORCEIA_ENV=production
export JWT_SECRET="$(openssl rand -hex 32)"
export ADMIN_PASSWORD='Senha!ForteCom12+'
export WEBHOOK_SECRET="$(openssl rand -hex 24)"
export FORCEIA_WEBHOOK_REQUIRE_KEY=1
export FORCEIA_DISABLE_LEGACY_TOKEN=1   # se não precisar de ADMIN_TOKEN
# NÃO use FORCEIA_ALLOW_WEAK_PASSWORD em prod
```

Webhook Evolution:

```
POST /webhook/evolution
X-Workspace-Key: <api_key do workspace>
X-Webhook-Secret: <WEBHOOK_SECRET>
```

## Módulos

- `agents/security.py` — rate limit, SSRF, headers, JWT check
- `agents/auth.py` — senha forte, JWT, legacy toggle
- `agents/webhook_server.py` — secret, rate limit, body cap
- `agents/scrapers/job_boards.py` — anti-SSRF

## Pendências recomendadas

- Redis rate-limit distribuído (multi-réplica)
- WAF / IP allowlist na frente do webhook (Evolution IPs)
- Rotação de JWT (refresh tokens)
- Secrets manager (não .env em disco em prod)
