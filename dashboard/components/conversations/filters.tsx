"use client";

import { cn } from "@/lib/utils";
import type { ConversationFilter } from "@/types/conversation";

const FILTERS: { id: ConversationFilter; label: string }[] = [
  { id: "all", label: "Todas" },
  { id: "ai", label: "IA" },
  { id: "attention", label: "Você" },
  { id: "human", label: "Humano" },
  { id: "closed", label: "Resolvidas" },
];

export function ConversationFilters({
  value,
  onChange,
  counts,
}: {
  value: ConversationFilter;
  onChange: (f: ConversationFilter) => void;
  counts: Record<ConversationFilter, number>;
}) {
  return (
    <div
      className="flex gap-0 overflow-x-auto border-b border-border"
      role="tablist"
      aria-label="Filtros"
    >
      {FILTERS.map((f) => {
        const active = value === f.id;
        const isAttention = f.id === "attention";
        return (
          <button
            key={f.id}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange(f.id)}
            className={cn(
              "shrink-0 border-b-2 px-2.5 py-1.5 text-[12px] transition-colors duration-100",
              active
                ? isAttention
                  ? "border-warning text-warning"
                  : "border-ink text-ink"
                : "border-transparent text-ink-soft hover:text-ink-muted",
            )}
          >
            {f.label}
            <span
              className={cn(
                "ml-1 text-mono",
                active && isAttention ? "text-warning" : "text-ink-soft",
              )}
            >
              {counts[f.id] ?? 0}
            </span>
          </button>
        );
      })}
    </div>
  );
}
