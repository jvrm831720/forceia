# Supabase - ForceIA

## 1. Criar projeto

1. Acesse https://supabase.com e crie um projeto
2. Em **Project Settings > API**, copie:
   - Project URL → `SUPABASE_URL`
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY` (backend only)

## 2. Criar tabelas

No **SQL Editor**, rode o arquivo:

```
supabase/schema.sql
```

Isso cria:
- `leads` (phone, stage, bant, ...)
- `messages` (historico)
- `events` (auditoria)

## 3. Configurar .env

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

Use a **service_role** no servidor dos agentes (webhook). Nao exponha no frontend.

## 4. Estagios (stage)

| stage | Agente |
|-------|--------|
| sdr | SDR |
| qualified | Closer |
| closer | Closer |
| followup | Follow-up |
| won / lost | terminal |

Transicoes automaticas via tags na resposta: `[QUALIFICADO]`, `[FECHADO]`, `[PERDIDO]`, `[FOLLOWUP]`.

## 5. Teste

```bash
cd agents
pip install -r requirements.txt
python run_sdr.py
```

As mensagens devem aparecer nas tabelas `leads` e `messages` no Supabase.
