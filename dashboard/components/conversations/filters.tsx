"use client";

import { cn } from "@/lib/utils";
import type { ConversationFilter } from "@/types/conversation";

const FILTERS: { id: ConversationFilter; label: string }[] = [
  { id: "all", label: "Todos" },
  { id: "ai_handling", label: "IA Atendendo" },
  { id: "needs_attention", label: "Precisa de Aten\u00e7\u00e3o" },
  { id: "human", label: "Humano" },
  { id: "finished", label: "Finalizadas" },
];

export function ConversationFilters({
  value,
  counts,
  onChange,
}: {
  value: ConversationFilter;
  counts: Record<ConversationFilter, number>;
  onChange: (filter: ConversationFilter) => void;
}) {
  return (
    <div
      className="flex gap-1.5 overflow-x-auto pb-0.5"
      role="tablist"
      aria-label="Filtrar conversas"
    >
      {FILTERS.map((f) => {
        const active = value === f.id;
        return (
          <button
            key={f.id}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange(f.id)}
            className={cn(
              "shrink-0 rounded-full px-3 py-1.5 text-[12px] font-semibold transition duration-200",
              active
                ? "bg-brand text-white shadow-card"
                : "bg-white text-ink-muted border border-border hover:text-ink hover:bg-border-soft"
            )}
          >
            {f.label}
            <span
              className={cn(
                "ml-1.5 tabular-nums",
                active ? "text-white/80" : "text-ink-soft"
              )}
            >
              {counts[f.id]}
            </span>
          </button>
        );
      })}
    </div>
  );
}
