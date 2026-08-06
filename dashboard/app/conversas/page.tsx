import { Header } from "@/components/layout/header";
import { Sidebar } from "@/components/layout/sidebar";
import { ConversationsShell } from "@/components/conversations/conversations-shell";
import { getConversations } from "@/lib/getConversations";

export default async function ConversasPage() {
  const data = await getConversations();

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />

      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <Header
          workspace={data.workspace}
          notificationsCount={data.notificationsCount}
        />

        <main className="flex min-h-0 flex-1 flex-col">
          <ConversationsShell data={data} />
        </main>
      </div>
    </div>
  );
}
