"use client";

import { cn } from "@/lib/utils";
import type { ConversationFilter } from "@/types/conversation";

const FILTERS: { id: ConversationFilter; label: string }[] = [
  { id: "all", label: "Todos" },
  { id: "ai", label: "IA Atendendo" },
  { id: "attention", label: "Atenção" },
  { id: "human", label: "Humano" },
  { id: "closed", label: "Finalizadas" },
];

export function ConversationFilters({
  value,
  onChange,
  counts,
}: {
  value: ConversationFilter;
  onChange: (filter: ConversationFilter) => void;
  counts: Record<ConversationFilter, number>;
}) {
  return (
    <div
      className="flex gap-1.5 overflow-x-auto pb-0.5 scrollbar-none"
      role="tablist"
      aria-label="Filtros de conversas"
    >
      {FILTERS.map((f) => {
        const active = value === f.id;
        const count = counts[f.id];
        return (
          <button
            key={f.id}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange(f.id)}
            className={cn(
              "inline-flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-[12px] font-semibold transition duration-200",
              active
                ? "bg-brand text-white shadow-card"
                : "bg-white text-ink-muted border border-border hover:text-ink hover:bg-border-soft"
            )}
          >
            {f.label}
            {count > 0 && (
              <span
                className={cn(
                  "inline-flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[10px] font-bold",
                  active ? "bg-white/25 text-white" : "bg-border-soft text-ink-muted"
                )}
              >
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
