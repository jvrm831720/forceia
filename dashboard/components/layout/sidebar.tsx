"use client";
import { cn } from "@/lib/utils";
import { CalendarDays, LayoutDashboard, LifeBuoy, MessageSquare, TrendingUp, Users } from "lucide-react";
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
    <aside className="hidden w-[220px] shrink-0 flex-col border-r border-border bg-background lg:flex">
      <div className="flex h-14 items-center gap-2.5 px-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-brand text-white">
          <span className="font-display text-xs font-bold tracking-tight">F</span>
        </div>
        <div className="min-w-0 leading-tight">
          <div className="font-display text-sm font-semibold tracking-tight text-ink">ForceIA</div>
          <div className="text-[11px] text-ink-soft">Equipe comercial IA</div>
        </div>
      </div>
      <nav className="flex flex-1 flex-col gap-0.5 px-2 py-2">
        <p className="mb-1 px-2 text-label">Operação</p>
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
          return (
            <Link key={href} href={href} className={cn(
              "group flex h-9 items-center gap-2.5 rounded-md px-2.5 text-sm transition-ui",
              active ? "bg-surface-strong font-medium text-ink" : "text-ink-muted hover:bg-surface-hover hover:text-ink",
            )}>
              <Icon className={cn("h-4 w-4 shrink-0", active ? "text-brand" : "text-ink-soft group-hover:text-ink-muted")} strokeWidth={1.75} />
              <span className="truncate">{label}</span>
              {active && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-brand" />}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-border px-3 py-3">
        <div className="flex items-center gap-2 px-1.5 py-1.5">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-40" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
          </span>
          <div className="min-w-0">
            <p className="text-xs font-medium text-ink">Agentes ativos</p>
            <p className="text-[11px] text-ink-soft">SDR · Closer · Follow-up</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
