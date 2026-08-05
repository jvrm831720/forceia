import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { MetricCard } from "@/types/dashboard";
import {
  CalendarCheck2,
  CircleCheck,
  Mail,
  ShieldAlert,
  Wallet,
} from "lucide-react";

const ICONS = {
  leads: Mail,
  qualified: CircleCheck,
  meetings: CalendarCheck2,
  pipeline: Wallet,
  approval: ShieldAlert,
} as const;

export function MetricCards({ metrics }: { metrics: MetricCard[] }) {
  return (
    <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
      {metrics.map((m) => {
        const Icon = ICONS[m.icon];
        const isSuccess = m.emphasis === "success";
        const isAlert = m.emphasis === "alert";

        return (
          <Card
            key={m.id}
            className={cn(
              "relative overflow-hidden p-5 transition hover:shadow-soft",
              isSuccess && "ring-1 ring-success/20",
              isAlert && "ring-1 ring-alert/20"
            )}
          >
            <div className="flex items-start justify-between gap-3">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-xl",
                  isSuccess && "bg-success-soft text-success",
                  isAlert && "bg-alert-soft text-alert",
                  !isSuccess && !isAlert && "bg-brand-soft text-brand"
                )}
              >
                <Icon className="h-5 w-5" strokeWidth={1.75} />
              </div>
              {m.delta && (
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 text-[11px] font-semibold",
                    m.deltaPositive === false
                      ? "bg-alert-soft text-alert"
                      : "bg-success-soft text-success"
                  )}
                >
                  {m.delta}
                </span>
              )}
            </div>

            <p className="mt-4 text-[13px] font-medium text-ink-muted">
              {m.label}
            </p>
            <p
              className={cn(
                "mt-1 font-display text-3xl font-semibold tracking-tight",
                isSuccess && "text-success",
                isAlert && "text-alert",
                !isSuccess && !isAlert && "text-ink"
              )}
            >
              {m.value}
            </p>
          </Card>
        );
      })}
    </section>
  );
}
