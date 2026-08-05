"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Loader2 } from "lucide-react";
import { login } from "@/lib/auth/login";
import type { AuthError } from "@/types/auth";
import { AuthAlert } from "./auth-alert";
import { AuthFooter } from "./auth-footer";
import { PasswordInput } from "./password-input";
import { cn } from "@/lib/utils";

const fieldClass =
  "h-9 w-full rounded-md border border-border bg-surface px-3 text-[13px] text-ink placeholder:text-ink-soft transition-ui duration-fast hover:border-[#2b2b2b] focus:border-brand focus:outline-none focus:shadow-focus disabled:cursor-not-allowed disabled:opacity-50";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AuthError | null>(null);
  const [errorKey, setErrorKey] = useState(0);
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

  const showError = (err: AuthError) => {
    setError(err);
    setErrorKey((k) => k + 1);
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
          showError(result.error);
        }
        return;
      }

      router.replace("/");
      router.refresh();
    } catch {
      showError({
        code: "connection_error",
        message:
          "Não foi possível acessar sua conta agora. Tente novamente em instantes.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-8 flex items-center gap-2.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-brand text-white">
          <span className="text-xs font-bold tracking-tight">F</span>
        </div>
        <span className="text-[15px] font-semibold tracking-tight text-ink">
          ForceIA
        </span>
      </div>

      <div className="mb-6">
        <h1 className="text-lg font-medium tracking-tight text-ink">
          Bem-vindo de volta
        </h1>
        <p className="mt-1 text-[13px] text-ink-muted">
          Acesse o Painel Cliente
        </p>
      </div>

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {error && (
          <AuthAlert key={errorKey} variant="error" shake>
            {error.message}
          </AuthAlert>
        )}

        <div>
          <label
            htmlFor="email"
            className="mb-1.5 block text-[12px] font-medium text-ink-muted"
          >
            E-mail
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (fieldErrors.email)
                setFieldErrors((f) => ({ ...f, email: undefined }));
            }}
            placeholder="seu@email.com"
            disabled={loading}
            aria-invalid={!!fieldErrors.email}
            aria-describedby={fieldErrors.email ? "email-error" : undefined}
            className={cn(
              fieldClass,
              fieldErrors.email &&
                "border-warning focus:border-warning focus:shadow-[0_0_0_2px_rgba(221,101,57,0.25)]",
            )}
          />
          {fieldErrors.email && (
            <p
              id="email-error"
              className="auth-field-error mt-1.5 text-[12px] text-warning"
            >
              {fieldErrors.email}
            </p>
          )}
        </div>

        <div>
          <div className="mb-1.5 flex items-center justify-between">
            <label
              htmlFor="password"
              className="block text-[12px] font-medium text-ink-muted"
            >
              Senha
            </label>
            <Link
              href="/esqueci-minha-senha"
              className="text-[12px] text-brand transition-ui duration-fast hover:opacity-80 active:opacity-70"
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
              className="auth-field-error mt-1.5 text-[12px] text-warning"
            >
              {fieldErrors.password}
            </p>
          )}
        </div>

        <label className="flex cursor-pointer items-center gap-2 pt-0.5">
          <input
            type="checkbox"
            checked={remember}
            onChange={(e) => setRemember(e.target.checked)}
            disabled={loading}
            className="h-3.5 w-3.5 rounded border-border bg-surface text-brand transition-ui duration-fast focus:ring-0 focus:ring-offset-0"
          />
          <span className="text-[12px] text-ink-muted">Manter conectado</span>
        </label>

        <button
          type="submit"
          disabled={loading}
          className={cn(
            "mt-2 flex h-9 w-full items-center justify-center gap-2 rounded-md text-[13px] font-medium",
            "bg-ink text-background",
            "transition-ui duration-fast",
            "hover:opacity-90",
            "active:scale-[0.99] active:opacity-80",
            "disabled:cursor-not-allowed disabled:opacity-50 disabled:active:scale-100",
            "focus-visible:outline-none focus-visible:shadow-focus",
          )}
        >
          {loading ? (
            <>
              <Loader2
                className="h-3.5 w-3.5 animate-spin"
                aria-hidden
              />
              Entrando…
            </>
          ) : (
            "Entrar"
          )}
        </button>
      </form>

      <div className="mt-8">
        <AuthFooter />
      </div>
    </div>
  );
}
