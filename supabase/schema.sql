-- ForceIA - Schema Supabase
-- Rode no SQL Editor do Supabase

-- Leads / contatos
create table if not exists leads (
  id uuid primary key default gen_random_uuid(),
  phone text not null unique,
  name text,
  company text,
  email text,
  stage text not null default 'sdr'
    check (stage in ('sdr', 'qualified', 'closer', 'followup', 'won', 'lost')),
  bant jsonb default '{}'::jsonb,
  metadata jsonb default '{}'::jsonb,
  last_message_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists leads_phone_idx on leads (phone);
create index if not exists leads_stage_idx on leads (stage);

-- Historico de mensagens
create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid not null references leads(id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  agent text, -- sdr | closer | followup
  created_at timestamptz not null default now()
);

create index if not exists messages_lead_id_idx on messages (lead_id);
create index if not exists messages_created_at_idx on messages (created_at);

-- Eventos / auditoria simples
create table if not exists events (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid references leads(id) on delete set null,
  type text not null,
  payload jsonb default '{}'::jsonb,
  created_at timestamptz not null default now()
);

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

-- RLS (service role bypassa; para anon/authenticated ajuste depois)
alter table leads enable row level security;
alter table messages enable row level security;
alter table events enable row level security;
