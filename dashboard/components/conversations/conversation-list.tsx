"use client";

import type { Conversation, ConversationFilter } from "@/types/conversation";
import { filterConversations } from "@/lib/conversation-utils";
import { ConversationItem } from "./conversation-item";
import { ConversationFilters } from "./filters";
import { ConversationSearch } from "./search";
import { ConversationsEmptyState } from "./empty-state";

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

  const counts: Partial<Record<ConversationFilter, number>> = {
    all: conversations.length,
    ai: conversations.filter((c) => c.status === "ai_handling").length,
    attention: conversations.filter((c) => c.status === "needs_attention").length,
    human: conversations.filter((c) => c.status === "human").length,
    closed: conversations.filter((c) => c.status === "closed").length,
  };

  return (
    <div className="flex h-full flex-col border-r border-border bg-surface-card">
      <div className="space-y-3 border-b border-border p-3">
        <ConversationSearch value={search} onChange={onSearchChange} />
        <ConversationFilters
          value={filter}
          onChange={onFilterChange}
          counts={counts}
        />
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {filtered.length === 0 ? (
          <ConversationsEmptyState
            title={search ? "Nenhum resultado" : "Nenhuma conversa"}
            description={
              search
                ? "Tente outro termo de busca."
                : "Seus agentes ainda não iniciaram atendimentos neste filtro."
            }
          />
        ) : (
          <div className="flex flex-col gap-0.5">
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
