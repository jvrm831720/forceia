import { Header } from "@/components/layout/header";
import { Sidebar } from "@/components/layout/sidebar";
import { Card } from "@/components/ui/card";

export function PlaceholderPage({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header
          workspace={{
            companyName: "Clínica Sol",
            userName: "João",
            userInitials: "JS",
          }}
        />
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl">
            <Card className="p-10 text-center">
              <h1 className="font-display text-2xl font-semibold text-ink">
                {title}
              </h1>
              <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-ink-muted">
                {description}
              </p>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
