"use client";

import type { WorkspaceInfo } from "@/types/dashboard";
import { Bell, Search } from "lucide-react";

interface HeaderProps {
  workspace: WorkspaceInfo;
  notificationsCount?: number;
}

export function Header({ workspace, notificationsCount = 0 }: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex h-11 items-center justify-between gap-3 border-b border-border bg-[var(--header)] px-3 backdrop-blur-md sm:px-4">
      <div className="flex min-w-0 items-center gap-3">
        <div className="min-w-0">
          <p className="truncate text-[13px] font-medium tracking-tight text-ink">
            {workspace.companyName}
          </p>
        </div>
        <div className="hidden items-center gap-1.5 sm:flex">
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-40" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-success" />
          </span>
          <span className="text-[11px] text-ink-soft">IA em operação</span>
        </div>
      </div>

      <div className="hidden max-w-xs flex-1 md:block">
        <label className="relative block">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-soft" />
          <input
            type="search"
            placeholder="Buscar…"
            className="h-7 w-full rounded-md border border-border bg-surface pl-8 pr-2.5 text-xs text-ink placeholder:text-ink-soft transition-ui focus:border-brand focus:outline-none focus:shadow-focus"
          />
        </label>
      </div>

      <div className="flex items-center gap-1.5">
        <button
          type="button"
          className="relative inline-flex h-7 w-7 items-center justify-center rounded-md text-ink-soft transition-ui hover:bg-surface-hover hover:text-ink"
          aria-label="Notificações"
        >
          <Bell className="h-3.5 w-3.5" strokeWidth={1.5} />
          {notificationsCount > 0 && (
            <span className="absolute right-0.5 top-0.5 h-1.5 w-1.5 rounded-full bg-warning" />
          )}
        </button>
        <div
          className="flex h-7 w-7 items-center justify-center rounded-md border border-border bg-surface text-[10px] font-semibold text-ink-muted"
          title={workspace.userName}
        >
          {workspace.userInitials}
        </div>
      </div>
    </header>
  );
}
