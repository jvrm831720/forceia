# Setup detalhado - ForceIA MVP

## 1. Variaveis de ambiente

Copie `.env.example` para `.env` e preencha:

- `OPENAI_API_KEY` (obrigatorio)
- `EVOLUTION_API_KEY` (mesmo valor usado no docker-compose)
- `EVOLUTION_INSTANCE` (nome da instancia criada na Evolution)

## 2. Subir Evolution API

```bash
docker compose up -d
```

Acesse http://localhost:8080 e:
1. Crie uma instancia (ex: forceia)
2. Conecte o WhatsApp via QR Code
3. Configure o webhook de mensagens para:
   `http://SEU_IP:8000/webhook/evolution`

(Para desenvolvimento local use ngrok ou similar.)

## 3. Rodar o webhook

```bash
cd agents
pip install -r requirements.txt
python webhook_server.py
```

## 4. Testar o SDR sem WhatsApp

```bash
python run_sdr.py
```

Converse no terminal para validar o prompt e o fluxo BANT.

## 5. Teste ponta a ponta

Envie uma mensagem do celular para o numero conectado na Evolution.
O webhook deve processar e responder automaticamente.
