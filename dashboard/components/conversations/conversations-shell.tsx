"use client";

import { useCallback, useMemo, useState } from "react";
import type {
  Conversation,
  ConversationFilter,
  ConversationsData,
} from "@/types/conversation";
import { ConversationList } from "./conversation-list";
import { ConversationView } from "./conversation-view";
import { ContextPanel } from "./context-panel";

type MobilePane = "list" | "thread" | "context";

export function ConversationsShell({ data }: { data: ConversationsData }) {
  const [conversations, setConversations] = useState<Conversation[]>(
    data.conversations
  );
  const [selectedId, setSelectedId] = useState<string | null>(
    data.conversations.find((c) => c.status === "needs_attention")?.id ??
      data.conversations[0]?.id ??
      null
  );
  const [filter, setFilter] = useState<ConversationFilter>("all");
  const [search, setSearch] = useState("");
  const [mobilePane, setMobilePane] = useState<MobilePane>("list");

  const selected = useMemo(
    () => conversations.find((c) => c.id === selectedId) ?? null,
    [conversations, selectedId]
  );

  const updateConversation = useCallback(
    (id: string, updater: (c: Conversation) => Conversation) => {
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? updater(c) : c))
      );
    },
    []
  );

  const handleSelect = (id: string) => {
    setSelectedId(id);
    setMobilePane("thread");
  };

  const handleAssume = () => {
    if (!selectedId) return;
    updateConversation(selectedId, (c) => ({
      ...c,
      status: "human",
      currentOwner: "human",
      handoff: c.handoff
        ? { ...c.handoff, dismissed: true }
        : undefined,
      messages: [
        ...c.messages,
        {
          id: `sys-${Date.now()}`,
          sender: "system",
          content: "Humano assumiu a conversa.",
          timestamp: new Date().toISOString(),
          systemKind: "assumed",
        },
      ],
      opportunity: { ...c.opportunity, currentOwner: "human" },
    }));
  };

  const handleReturnToAi = () => {
    if (!selectedId) return;
    updateConversation(selectedId, (c) => ({
      ...c,
      status: "ai_handling",
      currentOwner: "sdr",
      messages: [
        ...c.messages,
        {
          id: `sys-${Date.now()}`,
          sender: "system",
          content: "Conversa devolvida para SDR IA.",
          timestamp: new Date().toISOString(),
          systemKind: "returned",
        },
      ],
      opportunity: { ...c.opportunity, currentOwner: "sdr" },
    }));
  };

  const handleResolve = () => {
    if (!selectedId) return;
    updateConversation(selectedId, (c) => ({
      ...c,
      status: "closed",
      messages: [
        ...c.messages,
        {
          id: `sys-${Date.now()}`,
          sender: "system",
          content: "Conversa marcada como resolvida.",
          timestamp: new Date().toISOString(),
          systemKind: "note",
        },
      ],
    }));
  };

  const handleDismissHandoff = () => {
    if (!selectedId) return;
    updateConversation(selectedId, (c) => ({
      ...c,
      status: "ai_handling",
      handoff: c.handoff ? { ...c.handoff, dismissed: true } : undefined,
    }));
  };

  const handleSend = (text: string) => {
    if (!selectedId) return;
    updateConversation(selectedId, (c) => {
      return {
        ...c,
        status: "human",
        currentOwner: "human",
        lastMessage: text,
        lastMessageAt: new Date().toISOString(),
        messages: [
          ...c.messages,
          ...(c.currentOwner !== "human"
            ? [
                {
                  id: `sys-${Date.now()}`,
                  sender: "system" as const,
                  content: "Humano assumiu a conversa.",
                  timestamp: new Date().toISOString(),
                  systemKind: "assumed" as const,
                },
              ]
            : []),
          {
            id: `msg-${Date.now()}`,
            sender: "human" as const,
            content: text,
            timestamp: new Date().toISOString(),
            status: "sent" as const,
          },
        ],
        opportunity: { ...c.opportunity, currentOwner: "human" },
      };
    });
  };

  const handleAddNote = () => {
    if (!selectedId) return;
    updateConversation(selectedId, (c) => ({
      ...c,
      messages: [
        ...c.messages,
        {
          id: `sys-${Date.now()}`,
          sender: "system",
          content: "Nota interna adicionada.",
          timestamp: new Date().toISOString(),
          systemKind: "note",
        },
      ],
    }));
  };

  return (
    <div className="flex min-h-0 flex-1 overflow-hidden border-t border-border bg-background">
      {/* Column 1 — List */}
      <div
        className={`${
          mobilePane === "list" ? "flex" : "hidden"
        } w-full shrink-0 flex-col md:flex md:w-[300px] lg:w-[320px]`}
      >
        <ConversationList
          conversations={conversations}
          selectedId={selectedId}
          filter={filter}
          search={search}
          onFilterChange={setFilter}
          onSearchChange={setSearch}
          onSelect={handleSelect}
        />
      </div>

      {/* Column 2 — Thread */}
      <div
        className={`${
          mobilePane === "thread" ? "flex" : "hidden"
        } min-h-0 min-w-0 flex-1 flex-col md:flex`}
      >
        <ConversationView
          conversation={selected}
          onBack={() => setMobilePane("list")}
          onAssume={handleAssume}
          onReturnToAi={handleReturnToAi}
          onResolve={handleResolve}
          onAddNote={handleAddNote}
          onOpenLead={() => setMobilePane("context")}
          onDismissHandoff={handleDismissHandoff}
          onSend={handleSend}
        />
      </div>

      {/* Column 3 — Context / Decision */}
      <div
        className={`${
          mobilePane === "context" ? "flex" : "hidden"
        } min-h-0 w-full xl:flex xl:w-auto`}
      >
        <ContextPanel
          conversation={selected}
          onClose={() => setMobilePane("thread")}
        />
      </div>
    </div>
  );
}
