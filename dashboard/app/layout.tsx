import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ForceIA \u00b7 Dashboard",
  description:
    "Acompanhe sua equipe de vendas com IA em tempo real \u2014 leads, qualifica\u00e7\u00f5es, reuni\u00f5es e pipeline.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
