import type {
  AgentRole,
  Conversation,
  ConversationChannel,
  ConversationFilter,
  ConversationStatus,
  MessageSender,
  Temperature,
} from "@/types/conversation";

export function formatMessageTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "\u2014";
  return d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

export function formatListTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "\u2014";
  const now = new Date();
  const sameDay =
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate();
  if (sameDay) {
    return d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  }
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

export function formatDateSeparator(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "\u2014";
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const target = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const diff = (today.getTime() - target.getTime()) / 86400000;
  if (diff === 0) return "Hoje";
  if (diff === 1) return "Ontem";
  return d.toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

export function dateKey(iso: string): string {
  const d = new Date(iso);
  return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
}

export function agentLabel(role: AgentRole): string {
  if (role === "sdr") return "SDR IA";
  if (role === "closer") return "Closer IA";
  if (role === "followup") return "Follow-up IA";
  return "Humano";
}

export function agentBadgeVariant(
  role: AgentRole
): "success" | "ai" | "highlight" | "muted" {
  if (role === "sdr") return "success";
  if (role === "closer") return "ai";
  if (role === "followup") return "highlight";
  return "muted";
}

export function statusLabel(status: ConversationStatus): string {
  if (status === "ai_handling") return "IA atendendo";
  if (status === "needs_attention") return "Precisa de aten\u00e7\u00e3o";
  if (status === "human") return "Humano";
  return "Finalizada";
}

export function channelLabel(channel: ConversationChannel): string {
  if (channel === "whatsapp") return "WhatsApp";
  if (channel === "instagram") return "Instagram";
  return "Web";
}

export function temperatureLabel(t: Temperature): string {
  if (t === "hot") return "Quente";
  if (t === "warm") return "Morno";
  return "Frio";
}

export function temperatureVariant(
  t: Temperature
): "alert" | "highlight" | "muted" {
  if (t === "hot") return "alert";
  if (t === "warm") return "highlight";
  return "muted";
}

export function senderBubbleAlign(sender: MessageSender): "left" | "right" | "center" {
  if (sender === "system") return "center";
  if (sender === "lead") return "left";
  return "right";
}

export function filterConversations(
  items: Conversation[],
  filter: ConversationFilter,
  query: string
): Conversation[] {
  const q = query.trim().toLowerCase();
  return items.filter((c) => {
    if (filter !== "all" && c.status !== filter) return false;
    if (!q) return true;
    const hay = `${c.participant.name} ${c.participant.company} ${c.lastMessagePreview}`.toLowerCase();
    return hay.includes(q);
  });
}

export function filterCounts(items: Conversation[]): Record<ConversationFilter, number> {
  return {
    all: items.length,
    ai_handling: items.filter((c) => c.status === "ai_handling").length,
    needs_attention: items.filter((c) => c.status === "needs_attention").length,
    human: items.filter((c) => c.status === "human").length,
    finished: items.filter((c) => c.status === "finished").length,
  };
}
