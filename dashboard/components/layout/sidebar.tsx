"use client";

import { cn } from "@/lib/utils";
import {
  CalendarDays,
  LayoutDashboard,
  LifeBuoy,
  MessageSquare,
  TrendingUp,
  Users,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/conversas", label: "Conversas", icon: MessageSquare },
  { href: "/leads", label: "Leads", icon: Users },
  { href: "/agenda", label: "Agenda", icon: CalendarDays },
  { href: "/resultados", label: "Resultados", icon: TrendingUp },
  { href: "/suporte", label: "Suporte", icon: LifeBuoy },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-14 shrink-0 flex-col border-r border-border bg-background sm:flex">
      <div className="flex h-11 items-center justify-center border-b border-border">
        <Link
          href="/"
          className="flex h-7 w-7 items-center justify-center rounded-md bg-brand text-white"
          title="ForceIA"
        >
          <span className="text-[11px] font-bold tracking-tight">F</span>
        </Link>
      </div>

      <nav className="flex flex-1 flex-col items-center gap-0.5 py-2">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active =
            href === "/"
              ? pathname === "/"
              : pathname === href || pathname.startsWith(`${href}/`);
          return (
            <Link
              key={href}
              href={href}
              title={label}
              aria-label={label}
              className={cn(
                "group relative flex h-9 w-9 items-center justify-center rounded-md transition-ui",
                active
                  ? "bg-elevated text-ink"
                  : "text-ink-soft hover:bg-surface-hover hover:text-ink-muted",
              )}
            >
              <Icon className="h-[18px] w-[18px]" strokeWidth={1.5} />
              {active && (
                <span className="absolute left-0 top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-r bg-brand" />
              )}
              <span className="pointer-events-none absolute left-full z-50 ml-2 hidden whitespace-nowrap rounded-md border border-border bg-elevated px-2 py-1 text-[11px] text-ink group-hover:block">
                {label}
              </span>
            </Link>
          );
        })}
      </nav>

      <div className="flex flex-col items-center gap-2 border-t border-border py-3">
        <span className="relative flex h-1.5 w-1.5" title="Agentes ativos">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-50" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-success" />
        </span>
      </div>
    </aside>
  );
}
