-- ForceIA - Integrações (opcional)
-- Status também vive em workspaces.metadata (composio_session_id, pending_*).
-- Esta tabela é útil para auditoria e UI multi-provider no futuro.

create table if not exists workspace_integrations (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  provider text not null default 'composio',
  toolkit text not null,
  status text not null default 'disconnected'
    check (status in ('disabled', 'disconnected', 'pending', 'connected', 'error')),
  external_id text,
  display_name text,
  meta jsonb default '{}'::jsonb,
  connected_at timestamptz,
  updated_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  unique (workspace_id, provider, toolkit)
);

create index if not exists workspace_integrations_ws_idx
  on workspace_integrations (workspace_id);

create index if not exists workspace_integrations_toolkit_idx
  on workspace_integrations (toolkit);
