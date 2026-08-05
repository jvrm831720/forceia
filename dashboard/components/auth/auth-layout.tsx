import { AuthBrandPanel } from "./auth-brand-panel";

export function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background">
      {/* Brand panel — desktop / tablet */}
      <aside className="relative hidden w-[48%] shrink-0 border-r border-border bg-surface lg:flex lg:flex-col">
        <AuthBrandPanel />
      </aside>

      {/* Form area */}
      <main className="flex min-h-screen w-full flex-1 flex-col items-center justify-center px-4 py-10 sm:px-6 lg:px-10">
        {/* Mobile logo */}
        <div className="mb-8 flex items-center gap-2.5 lg:hidden">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand text-white shadow-card">
            <span className="font-display text-sm font-bold tracking-tight">
              F
            </span>
          </div>
          <div className="leading-tight">
            <div className="font-display text-[15px] font-semibold tracking-tight text-ink">
              ForceIA
            </div>
            <div className="text-[11px] text-ink-soft">
              Time de vendas com IA
            </div>
          </div>
        </div>

        <div className="w-full max-w-[400px]">{children}</div>
      </main>
    </div>
  );
}
