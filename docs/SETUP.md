# Setup ForceIA (multi-tenant)

## 1. Supabase

**Instalacao nova:** rode `supabase/schema.sql`  
**Ja tinha schema antigo:** rode `supabase/migrate_multitenant.sql`

Crie o workspace inicial:

```bash
cd agents
pip install -r requirements.txt
python create_workspace.py --name "Default" --slug default --instance forceia
```

## 2. .env

```bash
cp .env.example .env
```

Preencha Supabase + OpenAI. Opcional: Twenty e Evolution globais (fallback).

```env
DEFAULT_WORKSPACE_SLUG=default
```

## 3. Evolution + Webhook

```bash
docker compose up -d
python webhook_server.py
```

Webhook por instancia:
`https://SEU_HOST/webhook/evolution?instance=forceia`

ou header `X-Workspace-Key`.

## 4. Novo cliente (tenant)

```bash
python create_workspace.py --name "Clinica Sol" --slug clinica-sol --instance clinica-sol-wa
# criar instancia Evolution com mesmo nome
# apontar webhook da instancia
```

Ver `docs/MULTI_TENANT.md`.
