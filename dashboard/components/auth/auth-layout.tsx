import { AuthBrandPanel } from "./auth-brand-panel";

export function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background">
      {/* Product preview — desktop only */}
      <aside className="relative hidden w-[52%] shrink-0 overflow-hidden border-r border-border bg-[#0a0a0a] lg:block">
        <AuthBrandPanel />
      </aside>

      {/* Form column */}
      <main className="flex min-h-screen w-full flex-1 flex-col items-center justify-center px-6 py-12 sm:px-10">
        <div className="w-full max-w-[340px]">{children}</div>
      </main>
    </div>
  );
}
