"use client";

import Link from "next/link";
import { CheckCircle2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AuthFooter } from "./auth-footer";

export function ForgotPasswordSuccess({
  email,
  onResend,
  resendCooldown,
  resending,
}: {
  email: string;
  onResend: () => void;
  resendCooldown: number;
  resending: boolean;
}) {
  const canResend = resendCooldown <= 0 && !resending;

  return (
    <div className="rounded-lg border border-border bg-surface p-6 sm:p-8">
      <div className="mb-6 flex flex-col items-center text-center">
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-success-soft">
          <CheckCircle2 className="h-7 w-7 text-success" aria-hidden />
        </div>
        <h1 className="font-display text-xl font-semibold tracking-tight text-ink">
          Verifique seu e-mail
        </h1>
        <p className="mt-2 max-w-sm text-[13px] leading-relaxed text-ink-muted">
          Se existir uma conta vinculada a este endereço, você receberá as
          instruções para redefinir sua senha.
        </p>
        {email && (
          <p className="mt-3 rounded-lg bg-border-soft px-3 py-1.5 text-[13px] font-medium text-ink">
            {email}
          </p>
        )}
      </div>

      <div className="space-y-3" aria-live="polite">
        <Button asChild variant="primary" size="lg" className="w-full">
          <Link href="/login">Voltar para o Login</Link>
        </Button>

        <Button
          type="button"
          variant="secondary"
          size="lg"
          className="w-full"
          disabled={!canResend}
          onClick={onResend}
        >
          {resending ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              Reenviando…
            </>
          ) : resendCooldown > 0 ? (
            `Reenviar em ${resendCooldown}s`
          ) : (
            "Reenviar instruções"
          )}
        </Button>
      </div>

      <div className="mt-6 border-t border-border-soft pt-4">
        <AuthFooter />
      </div>
    </div>
  );
}
