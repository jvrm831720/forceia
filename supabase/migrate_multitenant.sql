-- Migracao: schema antigo (sem workspace) -> multi-tenant
-- Use apenas se voce ja rodou o schema.sql anterior

-- 1) Criar workspaces se nao existir
create table if not exists workspaces (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique,
  api_key text not null unique default encode(gen_random_bytes(24), 'hex'),
  evolution_instance text,
  evolution_api_url text,
  evolution_api_key text,
  twenty_api_url text,
  twenty_api_key text,
  openai_api_key text,
  gpt_model text default 'gpt-4o-mini',
  followup_stale_days int default 5,
  followup_min_hours int default 48,
  plan text default 'completo',
  active boolean not null default true,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 2) Workspace padrao para dados existentes
insert into workspaces (name, slug, evolution_instance)
select 'Default', 'default', 'forceia'
where not exists (select 1 from workspaces where slug = 'default');

-- 3) Adicionar workspace_id em leads
do $$
begin
  if not exists (
    select 1 from information_schema.columns
    where table_name = 'leads' and column_name = 'workspace_id'
  ) then
    alter table leads add column workspace_id uuid references workspaces(id);
    update leads set workspace_id = (select id from workspaces where slug = 'default' limit 1)
    where workspace_id is null;
    alter table leads alter column workspace_id set not null;
  end if;
end $$;

-- 4) Unique (workspace_id, phone)
alter table leads drop constraint if exists leads_phone_key;
do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'leads_workspace_id_phone_key'
  ) then
    alter table leads add constraint leads_workspace_id_phone_key unique (workspace_id, phone);
  end if;
end $$;

-- 5) workspace_id em events
do $$
begin
  if not exists (
    select 1 from information_schema.columns
    where table_name = 'events' and column_name = 'workspace_id'
  ) then
    alter table events add column workspace_id uuid references workspaces(id) on delete set null;
  end if;
end $$;
