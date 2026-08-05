import type { LoginCredentials, LoginResult } from "@/types/auth";

/**
 * Autenticação do Painel Cliente.
 *
 * Substitua o corpo desta função pela integração real
 * (API ForceIA, Supabase Auth, etc.).
 *
 * Não armazenar tokens em localStorage.
 * Preferir cookie httpOnly gerenciado no servidor.
 *
 * Em produção (`NODE_ENV === "production"`), o mock de demonstração
 * é desativado e retorna erro de conexão até a API real ser conectada.
 */
export async function login(
  credentials: LoginCredentials
): Promise<LoginResult> {
  const email = credentials.email.trim().toLowerCase();
  const password = credentials.password;

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return {
      ok: false,
      error: {
        code: "invalid_email",
        message: "Informe um e-mail válido.",
      },
    };
  }

  if (!password) {
    return {
      ok: false,
      error: {
        code: "empty_password",
        message: "Informe sua senha.",
      },
    };
  }

  // --- Integração real: substituir este bloco ---
  // Exemplo:
  // const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
  //   method: "POST",
  //   headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify({
  //     email,
  //     password,
  //     remember: credentials.remember,
  //   }),
  //   credentials: "include",
  // });
  // return mapApiLoginResult(res);

  if (process.env.NODE_ENV === "production") {
    return {
      ok: false,
      error: {
        code: "connection_error",
        message:
          "Autenticação ainda não está conectada à API. Contate a equipe ForceIA.",
      },
    };
  }

  await simulateNetwork();

  // Demo controlada (apenas em desenvolvimento):
  //  disabled@forceia.com → conta desativada
  //  fail@forceia.com → erro de conexão
  //  qualquer outro e-mail + senha "forceia" → sucesso
  if (email === "disabled@forceia.com") {
    return {
      ok: false,
      error: {
        code: "account_disabled",
        message:
          "Este acesso está desativado. Entre em contato com a equipe ForceIA.",
      },
    };
  }

  if (email === "fail@forceia.com") {
    return {
      ok: false,
      error: {
        code: "connection_error",
        message:
          "Não foi possível acessar sua conta agora. Tente novamente em instantes.",
      },
    };
  }

  if (password !== "forceia") {
    return {
      ok: false,
      error: {
        code: "invalid_credentials",
        message:
          "E-mail ou senha incorretos. Verifique os dados e tente novamente.",
      },
    };
  }

  return { ok: true };
}

function simulateNetwork(ms = 900): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
