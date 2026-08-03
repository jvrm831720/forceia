-- ForceIA - Tabelas do ciclo de auto-melhoria (rode no SQL Editor)
-- Depende do schema principal (workspaces, leads, messages)

-- Historico de execucoes do job de aprendizado
create table if not exists learning_runs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid references workspaces(id) on delete set null,
  status text not null default 'running'
    check (status in ('running', 'completed', 'failed', 'empty')),
  won_sampled int default 0,
  lost_sampled int default 0,
  summary text,
  error text,
  created_at timestamptz not null default now(),
  finished_at timestamptz
);

create index if not exists learning_runs_created_idx on learning_runs (created_at desc);

-- Sugestoes de prompt (gate humano)
create table if not exists prompt_suggestions (
  id uuid primary key default gen_random_uuid(),
  learning_run_id uuid references learning_runs(id) on delete set null,
  workspace_id uuid references workspaces(id) on delete cascade,
  agent text not null check (agent in ('sdr', 'closer', 'followup')),
  status text not null default 'pending'
    check (status in ('pending', 'approved', 'rejected', 'applied')),
  title text,
  rationale text,
  insights jsonb default '[]'::jsonb,
  metrics jsonb default '{}'::jsonb,
  current_prompt text not null,
  suggested_prompt text not null,
  diff_summary text,
  created_at timestamptz not null default now(),
  reviewed_at timestamptz,
  reviewed_note text
);

create index if not exists prompt_suggestions_status_idx on prompt_suggestions (status);
create index if not exists prompt_suggestions_workspace_idx on prompt_suggestions (workspace_id);

-- Overrides ativos por workspace (ou global se workspace_id is null)
create table if not exists agent_prompt_overrides (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid references workspaces(id) on delete cascade,
  agent text not null check (agent in ('sdr', 'closer', 'followup')),
  content text not null,
  source_suggestion_id uuid references prompt_suggestions(id) on delete set null,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (workspace_id, agent)
);

-- Unique parcial para override global (workspace_id null) no Postgres:
create unique index if not exists agent_prompt_overrides_global_agent_idx
  on agent_prompt_overrides (agent)
  where workspace_id is null;

alter table learning_runs enable row level security;
alter table prompt_suggestions enable row level security;
alter table agent_prompt_overrides enable row level security;
