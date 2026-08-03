"""
ForceIA - Webhook multi-tenant

Identifica o workspace por:
1. Header X-Workspace-Key (api_key do workspace)
2. Query ?instance= / body instance (Evolution instance name)
3. DEFAULT_WORKSPACE_SLUG no .env
"""

from fastapi import FastAPI, Header, HTTPException, Request
from dotenv import load_dotenv

from run_sdr import handle_incoming
from workspace_context import resolve_workspace

load_dotenv()

app = FastAPI(title="ForceIA Webhook Multi-tenant")


def extract_message(body: dict) -> tuple[str, str, str | None]:
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
    message = data.get("message") or {}
    text = (
        message.get("conversation")
        or (message.get("extendedTextMessage") or {}).get("text")
        or data.get("text")
        or ""
    )
    if key.get("fromMe"):
        return "", "", instance
    return number, (text or "").strip(), instance


@app.post("/webhook/evolution")
async def evolution_webhook(
    request: Request,
    x_workspace_key: str | None = Header(default=None, alias="X-Workspace-Key"),
):
    body = await request.json()
    event = str(body.get("event") or body.get("type") or "")

    if event and "message" not in event.lower():
        return {"status": "ignored", "event": event}

    number, text, instance = extract_message(body)
    query_instance = request.query_params.get("instance")
    instance = instance or query_instance

    ws = resolve_workspace(api_key=x_workspace_key, evolution_instance=instance)
    if not ws:
        raise HTTPException(status_code=401, detail="Workspace nao encontrado")

    if not number or not text:
        return {"status": "no_content", "workspace": ws.slug}

    reply = handle_incoming(number, text, workspace=ws, send=True)
    return {"status": "ok", "workspace": ws.slug, "reply": reply}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "forceia-webhook", "multi_tenant": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
