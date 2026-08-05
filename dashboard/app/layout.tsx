import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ForceIA · Operations",
  description:
    "Sistema operacional da sua equipe comercial com IA — pipeline, conversas, reuniões e resultados em tempo real.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="font-sans antialiased bg-background text-ink">{children}</body>
    </html>
  );
}
