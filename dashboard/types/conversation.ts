export type ConversationFilter =
  | "all"
  | "ai"
  | "attention"
  | "human"
  | "closed";

export type AgentRole = "sdr" | "closer" | "followup" | "human";

export type ConversationStatus =
  | "ai_handling"
  | "needs_attention"
  | "human"
  | "closed";

export type MessageSender = "lead" | "ai" | "human" | "system";

export type Channel = "whatsapp" | "email" | "webchat";

export type Temperature = "hot" | "warm" | "cold";

export interface ConversationMessage {
  id: string;
  sender: MessageSender;
  content: string;
  timestamp: string;
  status?: "sent" | "delivered" | "read";
  agentRole?: AgentRole;
  systemKind?:
    | "assumed"
    | "returned"
    | "stage_change"
    | "meeting"
    | "note";
}

export interface HandoffRequest {
  id: string;
  reason: string;
  requestedAt: string;
  dismissed?: boolean;
}

export interface MeetingInfo {
  date: string;
  time: string;
  link?: string;
  title?: string;
}

export interface TimelineEvent {
  id: string;
  label: string;
  timestamp: string;
  done: boolean;
}

export interface ConversationOpportunity {
  leadName: string;
  company: string;
  phone?: string;
  email?: string;
  source?: string;
  temperature: Temperature;
  pipelineStage: string;
  currentOwner: AgentRole;
  aiSummary: string;
  nextAction: string;
  lastActivity: string;
  meeting?: MeetingInfo;
  timeline: TimelineEvent[];
}

export interface Conversation {
  id: string;
  leadName: string;
  company: string;
  avatarInitials: string;
  lastMessage: string;
  lastMessageAt: string;
  channel: Channel;
  status: ConversationStatus;
  currentOwner: AgentRole;
  unreadCount?: number;
  messages: ConversationMessage[];
  opportunity: ConversationOpportunity;
  handoff?: HandoffRequest;
  isTyping?: "lead" | "ai" | null;
}

export interface ConversationsData {
  workspace: {
    companyName: string;
    userName: string;
    userInitials: string;
  };
  conversations: Conversation[];
  notificationsCount?: number;
}
