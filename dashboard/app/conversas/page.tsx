import { ConversationsShell } from "@/components/conversations/conversations-shell";
import { getConversations } from "@/lib/getConversations";

export const metadata = {
  title: "ForceIA \u00b7 Conversas",
  description: "Acompanhe sua equipe de vendas com IA em tempo real.",
};

export default async function ConversasPage() {
  const data = await getConversations();
  return <ConversationsShell data={data} />;
}
