"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { login } from "@/lib/auth/login";
import type { AuthError } from "@/types/auth";
import { AuthAlert } from "./auth-alert";
import { AuthFooter } from "./auth-footer";
import { PasswordInput } from "./password-input";
import { cn } from "@/lib/utils";

const inputClass =
  "h-11 w-full rounded-xl border border-border bg-white px-3.5 text-sm text-ink placeholder:text-ink-soft shadow-card transition focus:border-brand focus:outline-none focus:shadow-focus disabled:cursor-not-allowed disabled:opacity-60";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AuthError | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{
    email?: string;
    password?: string;
  }>({});

  const validate = () => {
    const next: { email?: string; password?: string } = {};
    const trimmed = email.trim();
    if (!trimmed || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      next.email = "Informe um e-mail válido.";
    }
    if (!password) {
      next.password = "Informe sua senha.";
    }
    setFieldErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!validate()) return;

    setLoading(true);
    try {
      const result = await login({
        email: email.trim(),
        password,
        remember,
      });

      if (!result.ok) {
        if (result.error.code === "invalid_email") {
          setFieldErrors({ email: result.error.message });
        } else if (result.error.code === "empty_password") {
          setFieldErrors({ password: result.error.message });
        } else {
          setError(result.error);
        }
        return;
      }

      router.replace("/");
      router.refresh();
    } catch {
      setError({
        code: "connection_error",
        message:
          "Não foi possível acessar sua conta agora. Tente novamente em instantes.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-border bg-surface-card p-6 shadow-card sm:p-8">
      <div className="mb-6">
        <h1 className="font-display text-xl font-semibold tracking-tight text-ink">
          Bem-vindo de volta
        </h1>
        <p className="mt-1.5 text-[13px] text-ink-muted">
          Acesse o Painel Cliente da ForceIA.
        </p>
      </div>

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {error && (
          <AuthAlert variant="error">{error.message}</AuthAlert>
        )}

        <div>
          <label
            htmlFor="email"
            className="mb-1.5 block text-[13px] font-medium text-ink"
          >
            E-mail
          </label>
          <input
            id="email"
            name="email"
            type="email"
            inputMode="email"
            autoComplete="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (fieldErrors.email)
                setFieldErrors((f) => ({ ...f, email: undefined }));
            }}
            placeholder="voce@empresa.com"
            disabled={loading}
            aria-invalid={!!fieldErrors.email}
            aria-describedby={fieldErrors.email ? "email-error" : undefined}
            className={cn(
              inputClass,
              fieldErrors.email &&
                "border-alert focus:border-alert focus:shadow-[0_0_0_3px_rgba(221,101,57,0.2)]"
            )}
          />
          {fieldErrors.email && (
            <p
              id="email-error"
              className="mt-1.5 text-[12px] text-alert"
              role="alert"
            >
              {fieldErrors.email}
            </p>
          )}
        </div>

        <div>
          <div className="mb-1.5 flex items-center justify-between gap-2">
            <label
              htmlFor="password"
              className="block text-[13px] font-medium text-ink"
            >
              Senha
            </label>
            <Link
              href="/esqueci-minha-senha"
              className="text-[12px] font-medium text-brand transition hover:underline"
            >
              Esqueci minha senha
            </Link>
          </div>
          <PasswordInput
            id="password"
            name="password"
            value={password}
            onChange={(v) => {
              setPassword(v);
              if (fieldErrors.password)
                setFieldErrors((f) => ({ ...f, password: undefined }));
            }}
            disabled={loading}
            aria-invalid={!!fieldErrors.password}
            aria-describedby={
              fieldErrors.password ? "password-error" : undefined
            }
          />
          {fieldErrors.password && (
            <p
              id="password-error"
              className="mt-1.5 text-[12px] text-alert"
              role="alert"
            >
              {fieldErrors.password}
            </p>
          )}
        </div>

        <label className="flex cursor-pointer items-center gap-2.5 select-none">
          <input
            type="checkbox"
            checked={remember}
            onChange={(e) => setRemember(e.target.checked)}
            disabled={loading}
            className="h-4 w-4 rounded border-border text-brand accent-brand focus:ring-brand focus:ring-offset-0"
          />
          <span className="text-[13px] text-ink-muted">Manter conectado</span>
        </label>

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
              Entrando…
            </>
          ) : (
            "Entrar"
          )}
        </Button>
      </form>

      <p className="mt-5 text-center text-[12px] leading-relaxed text-ink-soft">
        Seu acesso é criado pela equipe ForceIA durante a implantação.
      </p>

      <div className="mt-4 border-t border-border-soft pt-4">
        <AuthFooter />
      </div>
    </div>
  );
}
