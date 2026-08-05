import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { AgendaToday } from "@/components/dashboard/agenda-today";
import { AttentionList } from "@/components/dashboard/attention-list";
import { MetricCards } from "@/components/dashboard/metric-cards";
import { TeamSection } from "@/components/dashboard/team-section";
import { Header } from "@/components/layout/header";
import { Sidebar } from "@/components/layout/sidebar";
import { getDashboardData } from "@/lib/dashboard-data";

export default async function DashboardPage() {
  const data = await getDashboardData();

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col bg-canvas">
        <Header
          workspace={data.workspace}
          notificationsCount={data.notificationsCount}
        />
        <main className="flex-1 px-3 py-3 sm:px-4 sm:py-4">
          <div className="mx-auto flex max-w-7xl flex-col gap-3">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h1 className="text-[13px] font-medium tracking-tight text-ink">Operations</h1>
                <p className="text-[11px] text-ink-soft">Tempo real · {data.workspace.companyName}</p>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="relative flex h-1.5 w-1.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-40" />
                  <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-success" />
                </span>
                <span className="text-[11px] text-ink-soft">IA ativa</span>
              </div>
            </div>

            <MetricCards metrics={data.metrics} />

            <div className="grid gap-3 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <TeamSection agents={data.agents} />
              </div>
              <AttentionList items={data.attention} />
            </div>

            <div className="grid gap-3 lg:grid-cols-2">
              <ActivityFeed items={data.activity} />
              <AgendaToday items={data.agenda} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
