"""
ForceIA - Webhook multi-tenant (hardened)

Identifica o workspace por:
1. Header X-Workspace-Key (api_key do workspace) — preferido
2. Query ?instance= / body instance (Evolution instance name)
3. DEFAULT_WORKSPACE_SLUG no .env

Segurança:
- Rate limit por IP + workspace
- WEBHOOK_SECRET opcional (header X-Webhook-Secret ou query)
- Não devolve o texto completo da reply em produção
- Body size limitado
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from run_sdr import handle_incoming
from security import client_ip_from_headers, is_production, rate_limit_allow, security_headers
from workspace_context import resolve_workspace

load_dotenv()

app = FastAPI(title="ForceIA Webhook Multi-tenant")

MAX_BODY_BYTES = int(os.getenv("FORCEIA_WEBHOOK_MAX_BODY", "65536"))


@app.middleware("http")
async def _security_middleware(request: Request, call_next):
    response = await call_next(request)
    for k, v in security_headers().items():
        response.headers.setdefault(k, v)
    return response


def extract_message(body: dict) -> tuple[str, str, str | None, str | None]:
    data = body.get("data") or body
    instance = (
        body.get("instance")
        or data.get("instance")
        or (data.get("key") or {}).get("instance")
    )
    key = data.get("key") or {}
    remote_jid = key.get("remoteJid") or data.get("from") or ""
    number = (
        remote_jid.replace("@s.whatsapp.net", "")
        .replace("@g.us", "")
        .replace("+", "")
    )
    # só dígitos
    number = "".join(c for c in number if c.isdigit())
    message = data.get("message") or {}
    text = (
        message.get("conversation")
        or (message.get("extendedTextMessage") or {}).get("text")
        or data.get("text")
        or ""
    )
    msg_id = key.get("id") or data.get("messageId") or data.get("id")
    if key.get("fromMe"):
        return "", "", instance, msg_id
    return number, (text or "").strip()[:4000], instance, msg_id


def _webhook_secret_ok(request: Request, header_secret: str | None) -> bool:
    expected = (os.getenv("WEBHOOK_SECRET") or os.getenv("FORCEIA_WEBHOOK_SECRET") or "").strip()
    if not expected:
        # em produção exige secret
        if is_production():
            return False
        return True
    candidate = (
        header_secret
        or request.headers.get("x-webhook-secret")
        or request.query_params.get("secret")
        or ""
    ).strip()
    if not candidate:
        return False
    import secrets as sec

    return sec.compare_digest(candidate, expected)


@app.post("/webhook/evolution")
async def evolution_webhook(
    request: Request,
    x_workspace_key: str | None = Header(default=None, alias="X-Workspace-Key"),
    x_webhook_secret: str | None = Header(default=None, alias="X-Webhook-Secret"),
    x_forwarded_for: str | None = Header(default=None, alias="X-Forwarded-For"),
    x_real_ip: str | None = Header(default=None, alias="X-Real-IP"),
):
    if not _webhook_secret_ok(request, x_webhook_secret):
        raise HTTPException(status_code=401, detail="Webhook secret inválido ou ausente")

    ip = client_ip_from_headers(
        x_forwarded_for=x_forwarded_for, x_real_ip=x_real_ip, fallback="unknown"
    )
    if not rate_limit_allow(f"webhook:{ip}", limit=120, window_seconds=60):
        raise HTTPException(status_code=429, detail="Rate limit")

    raw = await request.body()
    if len(raw) > MAX_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Payload muito grande")

    try:
        import json

        body = json.loads(raw.decode("utf-8") if raw else "{}")
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido") from None

    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Body deve ser objeto JSON")

    event = str(body.get("event") or body.get("type") or "")
    if event and "message" not in event.lower():
        return {"status": "ignored", "event": event}

    number, text, instance, message_id = extract_message(body)
    query_instance = request.query_params.get("instance")
    instance = instance or query_instance

    # Preferir api_key; instance sozinho é mais fraco
    ws = resolve_workspace(api_key=x_workspace_key, evolution_instance=instance)
    if not ws:
        raise HTTPException(status_code=401, detail="Workspace nao encontrado")

    if not rate_limit_allow(f"webhook:ws:{ws.id}", limit=200, window_seconds=60):
        raise HTTPException(status_code=429, detail="Rate limit workspace")

    # Em produção, exige X-Workspace-Key se FORCEIA_WEBHOOK_REQUIRE_KEY=1
    require_key = (os.getenv("FORCEIA_WEBHOOK_REQUIRE_KEY") or "").strip().lower() in (
        "1",
        "true",
        "yes",
    ) or is_production()
    if require_key and not (x_workspace_key or "").strip():
        # ainda permite se WEBHOOK_SECRET válido (já checado)
        if not (os.getenv("WEBHOOK_SECRET") or os.getenv("FORCEIA_WEBHOOK_SECRET") or "").strip():
            raise HTTPException(
                status_code=401,
                detail="X-Workspace-Key obrigatório em produção",
            )

    if not number or not text:
        return {"status": "no_content", "workspace": ws.slug}

    reply = handle_incoming(
        number, text, workspace=ws, send=True, message_id=message_id
    )

    # Não vazar texto completo da IA em produção
    if is_production():
        return {
            "status": "ok",
            "workspace": ws.slug,
            "replied": bool(reply),
        }
    return {
        "status": "ok",
        "workspace": ws.slug,
        "reply": (reply or "")[:500],
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "forceia-webhook", "multi_tenant": True}


if __name__ == "__main__":
    import uvicorn

    if is_production() and not (
        os.getenv("WEBHOOK_SECRET") or os.getenv("FORCEIA_WEBHOOK_SECRET") or ""
    ).strip():
        print("AVISO: produção sem WEBHOOK_SECRET — defina para autenticar o webhook.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
