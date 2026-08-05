"use client";

import { ConversationFilters } from "@/components/conversations/filters";
import { ConversationItem } from "@/components/conversations/conversation-item";
import { ConversationsEmptyState } from "@/components/conversations/empty-state";
import { ConversationSearch } from "@/components/conversations/search";
import type { Conversation, ConversationFilter } from "@/types/conversation";

export function ConversationList({
  conversations,
  selectedId,
  filter,
  counts,
  query,
  onFilterChange,
  onQueryChange,
  onSelect,
}: {
  conversations: Conversation[];
  selectedId: string | null;
  filter: ConversationFilter;
  counts: Record<ConversationFilter, number>;
  query: string;
  onFilterChange: (f: ConversationFilter) => void;
  onQueryChange: (q: string) => void;
  onSelect: (id: string) => void;
}) {
  return (
    <aside
      className="flex h-full w-full flex-col border-r border-border bg-surface-card lg:w-[320px] lg:shrink-0"
      aria-label="Lista de conversas"
    >
      <div className="space-y-3 border-b border-border p-4">
        <div>
          <h1 className="font-display text-lg font-semibold tracking-tight text-ink">
            Conversas
          </h1>
          <p className="text-[12px] text-ink-muted">
            Sua equipe de IA em tempo real
          </p>
        </div>
        <ConversationSearch value={query} onChange={onQueryChange} />
        <ConversationFilters value={filter} counts={counts} onChange={onFilterChange} />
      </div>

      <div className="flex-1 space-y-1 overflow-y-auto p-2">
        {conversations.length === 0 ? (
          <ConversationsEmptyState
            title="Nada por aqui"
            description="Ajuste os filtros ou aguarde novas conversas da equipe IA."
          />
        ) : (
          conversations.map((c) => (
            <ConversationItem
              key={c.id}
              conversation={c}
              selected={selectedId === c.id}
              onSelect={onSelect}
            />
          ))
        )}
      </div>
    </aside>
  );
}
