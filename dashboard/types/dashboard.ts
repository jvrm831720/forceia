export type AgentStatus = "working" | "paused" | "offline";

export type Priority = "high" | "medium" | "low";

export type ActivityKind =
  | "qualified"
  | "meeting"
  | "followup"
  | "handoff"
  | "reply"
  | "pipeline";

export interface WorkspaceInfo {
  companyName: string;
  userName: string;
  userInitials: string;
  timezone?: string;
}

export interface MetricCard {
  id: string;
  label: string;
  value: string | number;
  delta?: string;
  deltaPositive?: boolean;
  icon: "leads" | "qualified" | "meetings" | "pipeline" | "approval";
  emphasis?: "success" | "alert" | "default";
}

export interface AgentCard {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  stats: { label: string; value: string | number }[];
}

export interface ActivityItem {
  id: string;
  time: string;
  kind: ActivityKind;
  title: string;
  description?: string;
}

export interface AttentionItem {
  id: string;
  name: string;
  company: string;
  reason: string;
  priority: Priority;
  conversationId: string;
}

export interface AgendaItem {
  id: string;
  time: string;
  company: string;
  contact?: string;
  owner: string;
  status: "confirmed" | "pending" | "completed";
}

export interface DashboardData {
  workspace: WorkspaceInfo;
  heroSummary: string;
  metrics: MetricCard[];
  agents: AgentCard[];
  activity: ActivityItem[];
  attention: AttentionItem[];
  agenda: AgendaItem[];
  notificationsCount?: number;
}
