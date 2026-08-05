import type { DashboardData } from "@/types/dashboard";

/**
 * Fonte de dados do Dashboard.
 * Substitua `getDashboardData` por fetch à API (ex.: /api/workspaces/:slug/dashboard).
 */
export async function getDashboardData(): Promise<DashboardData> {
  // Em produção: return fetch(...).then(r => r.json())
  return {
    workspace: {
      companyName: "Clínica Sol",
      userName: "João",
      userInitials: "JS",
    },
    heroSummary:
      "Hoje ela já respondeu 35 leads, qualificou 12 oportunidades, agendou 7 reuniões e gerou R$ 420.000 em pipeline.",
    metrics: [
      {
        id: "leads",
        label: "Leads atendidos",
        value: 35,
        delta: "+8 hoje",
        deltaPositive: true,
        icon: "leads",
      },
      {
        id: "qualified",
        label: "Qualificados",
        value: 12,
        delta: "+3",
        deltaPositive: true,
        icon: "qualified",
      },
      {
        id: "meetings",
        label: "Reuniões agendadas",
        value: 7,
        delta: "+2",
        deltaPositive: true,
        icon: "meetings",
      },
      {
        id: "pipeline",
        label: "Pipeline criado",
        value: "R$ 420.000",
        delta: "+18%",
        deltaPositive: true,
        icon: "pipeline",
        emphasis: "success",
      },
      {
        id: "approval",
        label: "Aguardando aprovação",
        value: 2,
        delta: "ação necessária",
        deltaPositive: false,
        icon: "approval",
        emphasis: "alert",
      },
    ],
    agents: [
      {
        id: "sdr",
        name: "SDR IA",
        role: "Prospecção e qualificação",
        status: "working",
        stats: [
          { label: "conversas", value: 18 },
          { label: "leads qualificados", value: 9 },
        ],
      },
      {
        id: "closer",
        name: "Closer IA",
        role: "Negociação e fechamento",
        status: "working",
        stats: [
          { label: "negociações", value: 5 },
          { label: "reuniões", value: 3 },
        ],
      },
      {
        id: "followup",
        name: "Follow-up IA",
        role: "Recuperação e nutrição",
        status: "working",
        stats: [
          { label: "follow-ups", value: 12 },
          { label: "leads recuperados", value: 4 },
        ],
      },
    ],
    activity: [
      {
        id: "a1",
        time: "09:42",
        kind: "qualified",
        title: "SDR IA qualificou Clínica Sorriso",
        description: "BANT completo \u00b7 score 78 \u00b7 ICP A",
      },
      {
        id: "a2",
        time: "09:51",
        kind: "meeting",
        title: "Closer IA marcou reunião",
        description: "Amanhã 15:00 \u00b7 Google Meet",
      },
      {
        id: "a3",
        time: "10:08",
        kind: "followup",
        title: "Follow-up recuperou um lead",
        description: "Lead parado há 11 dias voltou a responder",
      },
      {
        id: "a4",
        time: "10:14",
        kind: "handoff",
        title: "Cliente solicitou atendimento humano",
        description: "Prioridade alta \u00b7 aguardando você",
      },
      {
        id: "a5",
        time: "10:27",
        kind: "reply",
        title: "SDR IA respondeu Studio Forma",
        description: "Personalização com sinal de contratação",
      },
      {
        id: "a6",
        time: "10:41",
        kind: "pipeline",
        title: "Pipeline atualizado",
        description: "Oportunidade +R$ 48.000 \u00b7 plano Growth",
      },
      {
        id: "a7",
        time: "11:02",
        kind: "qualified",
        title: "SDR IA qualificou Mercado Verde",
        description: "Intent ready_to_buy \u00b7 score 84",
      },
      {
        id: "a8",
        time: "11:15",
        kind: "meeting",
        title: "Closer IA confirmou demo",
        description: "Hoje 16:30 \u00b7 com Ana Ribeiro",
      },
    ],
    attention: [
      {
        id: "att1",
        name: "Ricardo Mendes",
        company: "Clínica Sorriso",
        reason: "Pediu proposta customizada fora do playbook",
        priority: "high",
        conversationId: "c-1001",
      },
      {
        id: "att2",
        name: "Ana Ribeiro",
        company: "Studio Forma",
        reason: "Solicitou falar com um humano antes de agendar",
        priority: "high",
        conversationId: "c-1002",
      },
      {
        id: "att3",
        name: "Paulo Costa",
        company: "Mercado Verde",
        reason: "Objeção de preço após 3 tentativas da IA",
        priority: "medium",
        conversationId: "c-1003",
      },
    ],
    agenda: [
      {
        id: "m1",
        time: "14:00",
        company: "Clínica Sorriso",
        contact: "Ricardo Mendes",
        owner: "Closer IA",
        status: "confirmed",
      },
      {
        id: "m2",
        time: "15:30",
        company: "Studio Forma",
        contact: "Ana Ribeiro",
        owner: "Você",
        status: "pending",
      },
      {
        id: "m3",
        time: "16:30",
        company: "Mercado Verde",
        contact: "Paulo Costa",
        owner: "Closer IA",
        status: "confirmed",
      },
      {
        id: "m4",
        time: "17:45",
        company: "Alpha Odontologia",
        contact: "Mariana Luz",
        owner: "Closer IA",
        status: "confirmed",
      },
    ],
    notificationsCount: 3,
  };
}
