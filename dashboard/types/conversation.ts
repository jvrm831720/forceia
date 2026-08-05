export type ConversationChannel = "whatsapp" | "web" | "instagram";

export type AgentRole = "sdr" | "closer" | "followup" | "human";

export type ConversationStatus =
  | "ai_handling"
  | "needs_attention"
  | "human"
  | "finished";

export type MessageSender = "lead" | "ai" | "human" | "system";

export type ConversationFilter =
  | "all"
  | "ai_handling"
  | "needs_attention"
  | "human"
  | "finished";

export type Temperature = "hot" | "warm" | "cold";

export interface ConversationParticipant {
  id: string;
  name: string;
  company: string;
  phone?: string;
  email?: string;
  avatarUrl?: string;
  initials: string;
}

export interface ConversationMessage {
  id: string;
  sender: MessageSender;
  agentRole?: Exclude<AgentRole, "human">;
  content: string;
  createdAt: string;
  status?: "sent" | "delivered" | "read";
}

export interface ConversationTimelineEvent {
  id: string;
  label: string;
  at: string;
}

export interface ConversationMeeting {
  date: string;
  time: string;
  link?: string;
}

export interface ConversationOpportunity {
  origin: string;
  temperature: Temperature;
  pipelineStage: string;
  aiSummary: string;
  nextAction: string;
  lastActivityAt: string;
  meeting?: ConversationMeeting;
  timeline: ConversationTimelineEvent[];
}

export interface ConversationHandoff {
  requested: boolean;
  reason: string;
  requestedAt: string;
}

export interface Conversation {
  id: string;
  participant: ConversationParticipant;
  channel: ConversationChannel;
  status: ConversationStatus;
  responsible: AgentRole;
  lastMessagePreview: string;
  lastMessageAt: string;
  unreadCount: number;
  messages: ConversationMessage[];
  opportunity: ConversationOpportunity;
  handoff?: ConversationHandoff;
  typing?: "lead" | "ai" | null;
}

export interface ConversationsWorkspace {
  companyName: string;
  userName: string;
  userInitials: string;
}

export interface ConversationsData {
  workspace: ConversationsWorkspace;
  conversations: Conversation[];
  notificationsCount?: number;
}
