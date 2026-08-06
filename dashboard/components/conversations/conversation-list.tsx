"use client";

import type { Conversation, ConversationFilter } from "@/types/conversation";
import { filterConversations } from "@/lib/conversation-utils";
import { ConversationItem } from "./conversation-item";
import { ConversationFilters } from "./filters";
import { ConversationSearch } from "./search";
import { ConversationsEmptyState } from "./empty-state";

function buildFilterCounts(
  conversations: Conversation[],
): Record<ConversationFilter, number> {
  const counts: Record<ConversationFilter, number> = {
    all: 0,
    ai: 0,
    attention: 0,
    human: 0,
    closed: 0,
  };
  for (const c of conversations) {
    counts.all += 1;
    if (c.status === "ai_handling") counts.ai += 1;
    else if (c.status === "needs_attention") counts.attention += 1;
    else if (c.status === "human") counts.human += 1;
    else if (c.status === "closed") counts.closed += 1;
  }
  return counts;
}

export function ConversationList({
  conversations,
  selectedId,
  filter,
  search,
  onFilterChange,
  onSearchChange,
  onSelect,
}: {
  conversations: Conversation[];
  selectedId: string | null;
  filter: ConversationFilter;
  search: string;
  onFilterChange: (f: ConversationFilter) => void;
  onSearchChange: (q: string) => void;
  onSelect: (id: string) => void;
}) {
  const filtered = filterConversations(conversations, filter, search);
  const counts = buildFilterCounts(conversations);

  return (
    <div className="flex h-full flex-col border-r border-border bg-canvas">
      <div className="space-y-2 border-b border-border px-3 py-2.5">
        <div className="flex items-center justify-between">
          <h2 className="text-section text-ink">Conversas</h2>
          <span className="text-mono text-ink-soft">{counts.all}</span>
        </div>
        <ConversationSearch value={search} onChange={onSearchChange} />
        <ConversationFilters
          value={filter}
          onChange={onFilterChange}
          counts={counts}
        />
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {filtered.length === 0 ? (
          <ConversationsEmptyState
            title={search ? "Nenhum resultado" : "Nenhuma conversa neste filtro"}
            description={
              search
                ? "Tente outro termo."
                : "A equipe de IA ainda não iniciou atendimentos aqui."
            }
          />
        ) : (
          <div className="divide-y divide-border">
            {filtered.map((c) => (
              <ConversationItem
                key={c.id}
                conversation={c}
                selected={selectedId === c.id}
                onSelect={onSelect}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
