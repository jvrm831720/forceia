"use client";
import type { WorkspaceInfo } from "@/types/dashboard";
import { Bell, Menu, Search } from "lucide-react";

interface HeaderProps { workspace: WorkspaceInfo; notificationsCount?: number; }

export function Header({ workspace, notificationsCount = 0 }: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between gap-3 border-b border-border bg-[var(--header)] px-4 backdrop-blur-md sm:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <button type="button" className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-border bg-surface text-ink-muted transition-ui hover:text-ink lg:hidden" aria-label="Abrir menu">
          <Menu className="h-4 w-4" />
        </button>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold tracking-tight text-ink">{workspace.companyName}</p>
          <p className="hidden text-[11px] text-ink-soft sm:block">Operação em tempo real</p>
        </div>
      </div>
      <div className="hidden max-w-sm flex-1 md:block">
        <label className="relative block">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-soft" />
          <input type="search" placeholder="Buscar leads, conversas…" className="h-9 w-full rounded-md border border-border bg-surface pl-9 pr-3 text-sm text-ink placeholder:text-ink-soft transition-ui focus:border-brand focus:outline-none focus:shadow-focus" />
        </label>
      </div>
      <div className="flex items-center gap-2">
        <button type="button" className="relative inline-flex h-9 w-9 items-center justify-center rounded-md border border-border bg-surface text-ink-muted transition-ui hover:text-ink" aria-label="Notificações">
          <Bell className="h-4 w-4" strokeWidth={1.75} />
          {notificationsCount > 0 && (
            <span className="absolute -right-0.5 -top-0.5 flex h-3.5 min-w-3.5 items-center justify-center rounded-full bg-warning px-1 text-[9px] font-bold text-white">{notificationsCount}</span>
          )}
        </button>
        <div className="flex items-center gap-2 rounded-md border border-border bg-surface py-1 pl-1 pr-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-sm bg-ai-soft font-display text-[11px] font-bold text-ai">{workspace.userInitials}</div>
          <div className="hidden leading-tight sm:block">
            <p className="text-xs font-semibold text-ink">{workspace.userName}</p>
            <p className="text-[10px] text-ink-soft">Admin</p>
          </div>
        </div>
      </div>
    </header>
  );
}
