# Supabase - ForceIA (multi-tenant)

## 1. Criar projeto

1. Acesse https://supabase.com e crie um projeto
2. Em **Project Settings > API**, copie:
   - Project URL → `SUPABASE_URL`
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY` (backend only)

## 2. Criar tabelas

**Instalacao nova** — SQL Editor:

```
supabase/schema.sql
```

Cria:
- `workspaces` (clientes ForceIA)
- `leads` (por workspace)
- `messages`
- `events`

**Ja tinha schema antigo:**

```
supabase/migrate_multitenant.sql
```

## 3. Workspace inicial

```bash
cd agents
python create_workspace.py --name "Default" --slug default --instance forceia
```

## 4. .env

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
DEFAULT_WORKSPACE_SLUG=default
```

## 5. Estagios

| stage | Agente |
|-------|--------|
| sdr | SDR |
| qualified / closer | Closer |
| followup | Follow-up |
| won / lost | terminal |

Tags: `[QUALIFICADO]`, `[FECHADO]`, `[PERDIDO]`, `[FOLLOWUP]`

## 6. Validar

```bash
python validate_mvp.py
python run_sdr.py
```
