"""
ForceIA - Webhook Evolution API -> agentes + Supabase
"""

from fastapi import FastAPI, Request
from dotenv import load_dotenv

from run_sdr import handle_incoming

load_dotenv()

app = FastAPI(title="ForceIA Webhook")


def extract_message(body: dict) -> tuple[str, str]:
    data = body.get("data") or body
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
    # ignora mensagens enviadas por nos
    if key.get("fromMe"):
        return "", ""
    return number, (text or "").strip()


@app.post("/webhook/evolution")
async def evolution_webhook(request: Request):
    body = await request.json()
    event = str(body.get("event") or body.get("type") or "")

    if event and "message" not in event.lower():
        return {"status": "ignored", "event": event}

    number, text = extract_message(body)
    if not number or not text:
        return {"status": "no_content"}

    reply = handle_incoming(number, text, send=True)
    return {"status": "ok", "reply": reply}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "forceia-webhook"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
