"""
ForceIA - Webhook server para receber mensagens do Evolution API
e rotear para o agente SDR.
"""

import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from run_sdr import handle_incoming

load_dotenv()

app = FastAPI(title="ForceIA Webhook")

# Memoria simples em memoria (MVP). Em producao: Redis/DB.
conversations: dict[str, list] = {}


@app.post("/webhook/evolution")
async def evolution_webhook(request: Request):
    body = await request.json()

    # Evolution API envia eventos variados; filtramos mensagens recebidas
    event = body.get("event") or body.get("type")
    data = body.get("data") or body

    if event and "messages" not in str(event).lower() and "message" not in str(event).lower():
        return {"status": "ignored", "event": event}

    # Extrai numero e texto (formato pode variar conforme versao da Evolution)
    key = data.get("key") or {}
    remote_jid = key.get("remoteJid") or data.get("from") or ""
    number = remote_jid.replace("@s.whatsapp.net", "").replace("@g.us", "")

    message = data.get("message") or {}
    text = (
        message.get("conversation")
        or (message.get("extendedTextMessage") or {}).get("text")
        or data.get("text")
        or ""
    )

    if not number or not text:
        return {"status": "no_content"}

    history = conversations.get(number, [])
    reply = handle_incoming(number, text, history)

    history.append({"role": "user", "content": text})
    history.append({"role": "assistant", "content": reply})
    conversations[number] = history[-20:]  # limita historico

    return {"status": "ok", "reply": reply}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "forceia-webhook"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
