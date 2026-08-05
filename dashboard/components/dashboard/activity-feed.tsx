import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { ActivityItem, ActivityKind } from "@/types/dashboard";
import {
  CalendarCheck2,
  CircleCheck,
  MessageCircle,
  RefreshCw,
  UserRound,
  Wallet,
} from "lucide-react";

const KIND_META: Record<
  ActivityKind,
  { icon: typeof CircleCheck; className: string; label: string }
> = {
  qualified: {
    icon: CircleCheck,
    className: "bg-success-soft text-success",
    label: "Qualificação",
  },
  meeting: {
    icon: CalendarCheck2,
    className: "bg-brand-soft text-brand",
    label: "Reunião",
  },
  followup: {
    icon: RefreshCw,
    className: "bg-ai-soft text-ai",
    label: "Follow-up",
  },
  handoff: {
    icon: UserRound,
    className: "bg-alert-soft text-alert",
    label: "Handoff",
  },
  reply: {
    icon: MessageCircle,
    className: "bg-brand-soft text-brand",
    label: "Resposta",
  },
  pipeline: {
    icon: Wallet,
    className: "bg-success-soft text-success",
    label: "Pipeline",
  },
};

export function ActivityFeed({ items }: { items: ActivityItem[] }) {
  return (
    <Card className="h-full">
      <CardHeader>
        <div>
          <CardTitle>Atividade em tempo real</CardTitle>
          <p className="mt-1 text-sm text-ink-muted">
            O que sua equipe IA fez nos últimos minutos.
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-success-soft px-2.5 py-1 text-[11px] font-semibold text-success">
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-60" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-success" />
          </span>
          Ao vivo
        </span>
      </CardHeader>
      <CardContent>
        <ol className="relative space-y-0">
          {items.map((item, idx) => {
            const meta = KIND_META[item.kind];
            const Icon = meta.icon;
            const last = idx === items.length - 1;

            return (
              <li key={item.id} className="relative flex gap-4 pb-5 last:pb-0">
                {!last && (
                  <span className="absolute left-[19px] top-10 h-[calc(100%-28px)] w-px bg-border" />
                )}
                <div
                  className={cn(
                    "relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
                    meta.className
                  )}
                >
                  <Icon className="h-4 w-4" strokeWidth={1.75} />
                </div>
                <div className="min-w-0 flex-1 pt-0.5">
                  <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                    <time className="font-mono text-[12px] font-medium text-ink-soft">
                      {item.time}
                    </time>
                    <span className="text-[11px] font-medium uppercase tracking-wider text-ink-soft">
                      {meta.label}
                    </span>
                  </div>
                  <p className="mt-0.5 text-sm font-semibold text-ink">
                    {item.title}
                  </p>
                  {item.description && (
                    <p className="mt-0.5 text-[13px] text-ink-muted">
                      {item.description}
                    </p>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      </CardContent>
    </Card>
  );
}
