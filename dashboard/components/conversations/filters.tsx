"use client";

import { cn } from "@/lib/utils";
import type { ConversationFilter } from "@/types/conversation";

const FILTERS: { id: ConversationFilter; label: string }[] = [
  { id: "all", label: "Todas" },
  { id: "ai", label: "Em operação" },
  { id: "attention", label: "Precisa de você" },
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
    <div className="flex flex-wrap gap-1" role="tablist" aria-label="Filtros de conversa">
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
              "inline-flex items-center gap-1 rounded-sm border px-2 py-1 text-meta transition-ui duration-fast",
              active
                ? "border-border bg-elevated text-ink"
                : "border-transparent text-ink-soft hover:bg-surface hover:text-ink-muted",
            )}
          >
            {f.label}
            <span className="text-mono text-ink-soft">{counts[f.id] ?? 0}</span>
          </button>
        );
      })}
    </div>
  );
}
