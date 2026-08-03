"""
ForceIA - Agente SDR (MVP)
Qualifica leads e agenda reunioes via WhatsApp (Evolution API).
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import httpx

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "forceia-dev-key")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "forceia")

client = OpenAI(api_key=OPENAI_API_KEY)

SDR_SYSTEM_PROMPT = """Voce e o SDR da ForceIA, um time de vendas de IA.

Seu objetivo e:
1. Qualificar o lead usando BANT (Budget, Authority, Need, Timeline)
2. Entender a dor e o produto/servico de interesse
3. Quando o lead estiver qualificado, oferecer agenda de reuniao

Regras:
- Fale em portugues brasileiro, tom profissional e amigavel
- Faca no maximo 2-3 perguntas por mensagem
- Nao seja insistente demais
- Se o lead pedir para falar com humano, anote e confirme que sera transferido
- Sempre confirme dados importantes (nome, empresa, telefone se necessario)

Quando o lead estiver qualificado (BANT minimo), responda com:
[QUALIFICADO] e sugira horarios ou peca o melhor dia/horario.
"""


def send_whatsapp(number: str, text: str) -> dict:
    """Envia mensagem via Evolution API."""
    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "number": number,
        "text": text,
    }
    with httpx.Client(timeout=30) as http:
        r = http.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()


def sdr_reply(user_message: str, history: list[dict] | None = None) -> str:
    """Gera resposta do agente SDR."""
    messages = [{"role": "system", "content": SDR_SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=os.getenv("GPT_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content or ""


def handle_incoming(number: str, text: str, history: list[dict] | None = None) -> str:
    """Processa mensagem recebida e responde no WhatsApp."""
    reply = sdr_reply(text, history)
    send_whatsapp(number, reply)
    return reply


if __name__ == "__main__":
    # Teste local sem WhatsApp
    print("ForceIA SDR Agent - modo teste local")
    print("Digite mensagens (ou 'sair'):\n")
    history = []
    while True:
        user = input("Lead: ").strip()
        if user.lower() in ("sair", "exit", "quit"):
            break
        reply = sdr_reply(user, history)
        print(f"SDR: {reply}\n")
        history.append({"role": "user", "content": user})
        history.append({"role": "assistant", "content": reply})
