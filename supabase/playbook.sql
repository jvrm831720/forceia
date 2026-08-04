-- ForceIA — Playbook por workspace (Prioridade 1)
-- Rode no SQL Editor do Supabase (idempotente)

alter table workspaces
  add column if not exists playbook jsonb not null default '{}'::jsonb;

comment on column workspaces.playbook is
  'Playbook comercial do cliente: ICP, persona, pricing, cases, objeções, tom, FAQ';

create index if not exists workspaces_playbook_gin_idx
  on workspaces using gin (playbook);
