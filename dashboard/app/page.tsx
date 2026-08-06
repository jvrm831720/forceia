import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { AgendaToday } from "@/components/dashboard/agenda-today";
import { AgentStage } from "@/components/dashboard/agent-stage";
import { AttentionList } from "@/components/dashboard/attention-list";
import { MetricCards } from "@/components/dashboard/metric-cards";
import { OpsBrief } from "@/components/dashboard/ops-brief";
import { OpsChart } from "@/components/dashboard/ops-chart";
import { Header } from "@/components/layout/header";
import { Sidebar } from "@/components/layout/sidebar";
import { getDashboardData } from "@/lib/dashboard-data";

/**
 * Dashboard narrative (ForceIA identity):
 * 1. How is the operation?     → OpsBrief
 * 2. Who is working?           → AgentStage (center of product)
 * 3. What needs me?            → AttentionList
 * 4. What changed?             → OpsChart + KPIs
 * 5. What did AI do / next?    → Activity + Agenda
 */
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
        <main className="flex-1 px-3 py-3 sm:px-4">
          <div className="mx-auto flex max-w-7xl flex-col gap-3">
            <OpsBrief
              workspace={data.workspace}
              summary={data.heroSummary}
            />
            <AgentStage agents={data.agents} />
            <AttentionList items={data.attention} />
            <OpsChart />
            <MetricCards metrics={data.metrics} />
            <div className="grid gap-3 lg:grid-cols-5">
              <div className="lg:col-span-3">
                <ActivityFeed items={data.activity} />
              </div>
              <div className="lg:col-span-2">
                <AgendaToday items={data.agenda} />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
