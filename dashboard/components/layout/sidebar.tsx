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
    <aside className="hidden lg:flex w-[248px] shrink-0 flex-col border-r border-border bg-surface-card">
      <div className="flex h-16 items-center gap-2.5 px-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-brand text-white shadow-card">
          <span className="font-display text-sm font-bold tracking-tight">F</span>
        </div>
        <div className="leading-tight">
          <div className="font-display text-[15px] font-semibold tracking-tight text-ink">
            ForceIA
          </div>
          <div className="text-[11px] text-ink-soft">Time de vendas com IA</div>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-0.5 px-3 py-3">
        {NAV.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
                active
                  ? "bg-brand-soft text-brand"
                  : "text-ink-muted hover:bg-border-soft hover:text-ink"
              )}
            >
              <Icon
                className={cn(
                  "h-[18px] w-[18px]",
                  active ? "text-brand" : "text-ink-soft group-hover:text-ink"
                )}
                strokeWidth={1.75}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="m-3 rounded-2xl border border-border bg-surface p-4">
        <div className="mb-1 flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
          </span>
          <span className="text-xs font-semibold text-ink">Equipe ativa</span>
        </div>
        <p className="text-[12px] leading-relaxed text-ink-muted">
          Seus agentes respondem, qualificam e agendam sem pausa.
        </p>
      </div>
    </aside>
  );
}
