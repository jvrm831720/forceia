-- ForceIA - Schema Supabase (multi-tenant)
-- Rode no SQL Editor do Supabase

-- Workspaces (clientes ForceIA)
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
  playbook jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists workspaces_slug_idx on workspaces (slug);
create index if not exists workspaces_api_key_idx on workspaces (api_key);
create index if not exists workspaces_evolution_instance_idx on workspaces (evolution_instance);

-- Leads / contatos (por workspace)
create table if not exists leads (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references leads(id) on delete cascade,
  phone text not null,
  name text,
  company text,
  email text,
  stage text not null default 'sdr'
    check (stage in ('sdr', 'qualified', 'closer', 'followup', 'won', 'lost')),
  bant jsonb default '{}'::jsonb,
  metadata jsonb default '{}'::jsonb,
  last_message_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (workspace_id, phone)
);

create index if not exists leads_phone_idx on leads (phone);
create index if not exists leads_stage_idx on leads (stage);
create index if not exists leads_workspace_id_idx on leads (workspace_id);
create index if not exists leads_workspace_stage_idx on leads (workspace_id, stage);

-- Historico de mensagens
create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid not null references leads(id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  agent text,
  created_at timestamptz not null default now()
);

create index if not exists messages_lead_id_idx on messages (lead_id);
create index if not exists messages_created_at_idx on messages (created_at);

-- Eventos / auditoria
create table if not exists events (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid references workspaces(id) on delete set null,
  lead_id uuid references leads(id) on delete set null,
  type text not null,
  payload jsonb default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists events_workspace_id_idx on events (workspace_id);

-- Trigger updated_at
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists leads_updated_at on leads;
create trigger leads_updated_at
  before update on leads
  for each row execute function set_updated_at();

drop trigger if exists workspaces_updated_at on workspaces;
create trigger workspaces_updated_at
  before update on workspaces
  for each row execute function set_updated_at();

-- RLS basico
alter table workspaces enable row level security;
alter table leads enable row level security;
alter table messages enable row level security;
alter table events enable row level security;

-- Workspace demo (opcional — troque o nome)
-- insert into workspaces (name, slug, evolution_instance)
-- values ('Demo ForceIA', 'demo', 'forceia');
