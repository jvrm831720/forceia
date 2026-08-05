"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { requestPasswordReset } from "@/lib/auth/request-password-reset";
import type { AuthError } from "@/types/auth";
import { AuthAlert } from "./auth-alert";
import { AuthFooter } from "./auth-footer";
import { ForgotPasswordSuccess } from "./forgot-password-success";
import { cn } from "@/lib/utils";

const COOLDOWN_SECONDS = 45;

const inputClass =
  "h-11 w-full rounded-xl border border-border bg-white px-3.5 text-sm text-ink placeholder:text-ink-soft shadow-card transition focus:border-brand focus:outline-none focus:shadow-focus disabled:cursor-not-allowed disabled:opacity-60";

export function ForgotPasswordForm() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<AuthError | null>(null);
  const [fieldError, setFieldError] = useState<string | null>(null);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [resending, setResending] = useState(false);

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const t = setTimeout(() => setResendCooldown((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [resendCooldown]);

  const submit = useCallback(async (isResend = false) => {
    setError(null);
    setFieldError(null);

    const trimmed = email.trim();
    if (!trimmed || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      setFieldError("Informe um e-mail válido.");
      return;
    }

    if (isResend) setResending(true);
    else setLoading(true);

    try {
      const result = await requestPasswordReset({ email: trimmed });

      if (!result.ok) {
        if (result.error.code === "invalid_email") {
          setFieldError(result.error.message);
        } else {
          setError(result.error);
        }
        return;
      }

      setSent(true);
      setResendCooldown(COOLDOWN_SECONDS);
    } catch {
      setError({
        code: "connection_error",
        message:
          "Não foi possível enviar as instruções agora. Tente novamente em instantes.",
      });
    } finally {
      setLoading(false);
      setResending(false);
    }
  }, [email]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submit(false);
  };

  if (sent) {
    return (
      <ForgotPasswordSuccess
        email={email.trim()}
        onResend={() => submit(true)}
        resendCooldown={resendCooldown}
        resending={resending}
      />
    );
  }

  return (
    <div className="rounded-2xl border border-border bg-surface-card p-6 shadow-card sm:p-8">
      <div className="mb-6">
        <h1 className="font-display text-xl font-semibold tracking-tight text-ink">
          Recupere seu acesso
        </h1>
        <p className="mt-1.5 text-[13px] leading-relaxed text-ink-muted">
          Informe o e-mail vinculado à sua conta. Enviaremos as instruções para
          redefinir sua senha.
        </p>
      </div>

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {error && <AuthAlert variant="error">{error.message}</AuthAlert>}

        <div>
          <label
            htmlFor="reset-email"
            className="mb-1.5 block text-[13px] font-medium text-ink"
          >
            E-mail
          </label>
          <input
            id="reset-email"
            name="email"
            type="email"
            inputMode="email"
            autoComplete="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (fieldError) setFieldError(null);
            }}
            placeholder="voce@empresa.com"
            disabled={loading}
            aria-invalid={!!fieldError}
            aria-describedby={fieldError ? "reset-email-error" : undefined}
            className={cn(
              inputClass,
              fieldError &&
                "border-alert focus:border-alert focus:shadow-[0_0_0_3px_rgba(221,101,57,0.2)]"
            )}
          />
          {fieldError && (
            <p
              id="reset-email-error"
              className="mt-1.5 text-[12px] text-alert"
              role="alert"
            >
              {fieldError}
            </p>
          )}
        </div>

        <Button
          type="submit"
          variant="primary"
          size="lg"
          disabled={loading}
          className="w-full"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              Enviando…
            </>
          ) : (
            "Enviar instruções"
          )}
        </Button>
      </form>

      <p className="mt-5 text-[12px] leading-relaxed text-ink-soft">
        Por segurança, a mensagem exibida será a mesma mesmo que o e-mail não
        esteja cadastrado.
      </p>

      <div className="mt-5">
        <Link
          href="/login"
          className="inline-flex items-center gap-1.5 text-[13px] font-medium text-ink-muted transition hover:text-brand"
        >
          <ArrowLeft className="h-3.5 w-3.5" aria-hidden />
          Voltar para o Login
        </Link>
      </div>

      <div className="mt-5 border-t border-border-soft pt-4">
        <AuthFooter />
      </div>
    </div>
  );
}
