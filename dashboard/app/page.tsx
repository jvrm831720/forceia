import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { AgendaToday } from "@/components/dashboard/agenda-today";
import { AttentionList } from "@/components/dashboard/attention-list";
import { MetricCards } from "@/components/dashboard/metric-cards";
import { OpsChart } from "@/components/dashboard/ops-chart";
import { OpsToolbar } from "@/components/dashboard/ops-toolbar";
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
            <OpsToolbar workspace={data.workspace} />
            <OpsChart />
            <MetricCards metrics={data.metrics} />
            <div className="grid gap-3 lg:grid-cols-5">
              <div className="lg:col-span-3">
                <ActivityFeed items={data.activity} />
              </div>
              <div className="lg:col-span-2">
                <AttentionList items={data.attention} />
              </div>
            </div>
            <TeamSection agents={data.agents} />
            <AgendaToday items={data.agenda} />
          </div>
        </main>
      </div>
    </div>
  );
}
