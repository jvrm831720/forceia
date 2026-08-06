import type {
  AgentRole,
  Conversation,
  ConversationFilter,
  ConversationStatus,
  MessageSender,
} from "@/types/conversation";

export function agentLabel(role: AgentRole): string {
  switch (role) {
    case "sdr":
      return "SDR IA";
    case "closer":
      return "Closer IA";
    case "followup":
      return "Follow-up IA";
    case "human":
      return "Humano";
  }
}

export function agentBadgeVariant(
  role: AgentRole
): "success" | "ai" | "highlight" | "muted" {
  switch (role) {
    case "sdr":
      return "success";
    case "closer":
      return "ai";
    case "followup":
      return "highlight";
    case "human":
      return "muted";
  }
}

export function statusLabel(status: ConversationStatus): string {
  switch (status) {
    case "ai_handling":
      return "Em operação";
    case "needs_attention":
      return "Precisa de você";
    case "human":
      return "Cobertura humana";
    case "closed":
      return "Resolvida";
  }
}

/** Código operacional mono (Product Language). */
export function statusCode(status: ConversationStatus): string {
  switch (status) {
    case "ai_handling":
      return "AI";
    case "needs_attention":
      return "HO";
    case "human":
      return "HUM";
    case "closed":
      return "DONE";
  }
}

export function channelLabel(channel: Conversation["channel"]): string {
  switch (channel) {
    case "whatsapp":
      return "WhatsApp";
    case "email":
      return "E-mail";
    case "webchat":
      return "Web";
  }
}

export function formatMessageTime(iso: string): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";

  const now = new Date();
  const sameDay =
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate();

  if (sameDay) {
    return d.toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  const isYesterday =
    d.getFullYear() === yesterday.getFullYear() &&
    d.getMonth() === yesterday.getMonth() &&
    d.getDate() === yesterday.getDate();

  if (isYesterday) return "Ontem";

  return d.toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "short",
  });
}

export function formatListTime(iso: string): string {
  return formatMessageTime(iso);
}

export function dateKey(iso: string): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
  });
}

export function senderBubbleAlign(
  sender: MessageSender
): "left" | "right" | "center" {
  switch (sender) {
    case "lead":
      return "left";
    case "ai":
    case "human":
      return "right";
    case "system":
      return "center";
  }
}

export function filterConversations(
  items: Conversation[],
  filter: ConversationFilter,
  search: string
): Conversation[] {
  const q = search.trim().toLowerCase();

  return items.filter((c) => {
    if (filter === "ai" && c.status !== "ai_handling") return false;
    if (filter === "attention" && c.status !== "needs_attention") return false;
    if (filter === "human" && c.status !== "human") return false;
    if (filter === "closed" && c.status !== "closed") return false;

    if (!q) return true;

    return (
      c.leadName.toLowerCase().includes(q) ||
      c.company.toLowerCase().includes(q) ||
      c.lastMessage.toLowerCase().includes(q)
    );
  });
}

export function temperatureLabel(
  t: Conversation["opportunity"]["temperature"]
): string {
  switch (t) {
    case "hot":
      return "Quente";
    case "warm":
      return "Morno";
    case "cold":
      return "Frio";
  }
}
