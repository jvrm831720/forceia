"use client";

import type { WorkspaceInfo } from "@/types/dashboard";
import { Bell, Menu, Search } from "lucide-react";

export function Header({
  workspace,
  notificationsCount = 0,
}: {
  workspace: WorkspaceInfo;
  notificationsCount?: number;
}) {
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-4 border-b border-border bg-surface/80 px-4 backdrop-blur-md sm:px-6 lg:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <button
          type="button"
          className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-white text-ink-muted lg:hidden"
          aria-label="Abrir menu"
        >
          <Menu className="h-4 w-4" />
        </button>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-ink">
            {workspace.companyName}
          </p>
          <p className="hidden text-[11px] text-ink-soft sm:block">
            Operação comercial em tempo real
          </p>
        </div>
      </div>

      <div className="hidden max-w-md flex-1 md:block">
        <label className="relative block">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-soft" />
          <input
            type="search"
            placeholder="Buscar leads, empresas, conversas…"
            className="h-10 w-full rounded-xl border border-border bg-white pl-10 pr-3 text-sm text-ink placeholder:text-ink-soft shadow-card focus:border-brand focus:outline-none focus:shadow-focus"
          />
        </label>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        <button
          type="button"
          className="relative inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-white text-ink-muted shadow-card transition hover:text-ink"
          aria-label="Notificações"
        >
          <Bell className="h-4 w-4" strokeWidth={1.75} />
          {notificationsCount > 0 && (
            <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-alert px-1 text-[10px] font-bold text-white">
              {notificationsCount}
            </span>
          )}
        </button>

        <div className="flex items-center gap-2.5 rounded-xl border border-border bg-white py-1.5 pl-1.5 pr-3 shadow-card">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-ai-soft font-display text-xs font-bold text-ai">
            {workspace.userInitials}
          </div>
          <div className="hidden leading-tight sm:block">
            <p className="text-sm font-semibold text-ink">{workspace.userName}</p>
            <p className="text-[11px] text-ink-soft">Admin</p>
          </div>
        </div>
      </div>
    </header>
  );
}
