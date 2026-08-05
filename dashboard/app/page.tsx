import { ActivityFeed } from "@/components/dashboard/activity-feed";
import { AgendaToday } from "@/components/dashboard/agenda-today";
import { AttentionList } from "@/components/dashboard/attention-list";
import { Hero } from "@/components/dashboard/hero";
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
      <div className="flex min-w-0 flex-1 flex-col">
        <Header workspace={data.workspace} notificationsCount={data.notificationsCount} />
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <div className="mx-auto flex max-w-6xl flex-col gap-8">
            <Hero workspace={data.workspace} summary={data.heroSummary} />
            <MetricCards metrics={data.metrics} />
            <TeamSection agents={data.agents} />
            <div className="grid gap-4 lg:grid-cols-2">
              <ActivityFeed items={data.activity} />
              <AttentionList items={data.attention} />
            </div>
            <AgendaToday items={data.agenda} />
          </div>
        </main>
      </div>
    </div>
  );
}
