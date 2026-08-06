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

/** Midday-style tabs: text-sm, active medium, muted inactive. */
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
    <div className="flex items-center gap-1" role="tablist" aria-label="Filtros">
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
              "px-2.5 py-1.5 text-sm transition-colors",
              active
                ? isAttention
                  ? "font-medium text-warning"
                  : "font-medium text-ink"
                : "text-ink-soft hover:text-ink-muted",
            )}
          >
            {f.label}
            <span
              className={cn(
                "ml-1.5 font-mono text-xs",
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
