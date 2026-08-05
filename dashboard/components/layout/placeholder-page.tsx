import { Header } from "@/components/layout/header";
import { Sidebar } from "@/components/layout/sidebar";
import { getDashboardData } from "@/lib/dashboard-data";

interface PlaceholderPageProps { title: string; description: string; }

export async function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  const data = await getDashboardData();
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header workspace={data.workspace} notificationsCount={data.notificationsCount} />
        <main className="flex flex-1 items-center justify-center px-4 py-16">
          <div className="max-w-md text-center">
            <p className="text-label mb-3">Em breve</p>
            <h1 className="font-display text-2xl font-semibold tracking-tight text-ink">{title}</h1>
            <p className="mt-2 text-sm leading-relaxed text-ink-muted">{description}</p>
          </div>
        </main>
      </div>
    </div>
  );
}
