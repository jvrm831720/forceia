import type { PasswordResetRequest, PasswordResetResult } from "@/types/auth";

/**
 * Solicitação de redefinição de senha.
 *
 * Sempre retorna sucesso genérico (exceto validação e erro de conexão simulado)
 * para não revelar se o e-mail existe.
 * Substitua o corpo pela integração real (API ForceIA / provedor de auth).
 *
 * Em produção (`NODE_ENV === "production"`), o mock é desativado.
 */
export async function requestPasswordReset(
  request: PasswordResetRequest
): Promise<PasswordResetResult> {
  const email = request.email.trim().toLowerCase();

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return {
      ok: false,
      error: {
        code: "invalid_email",
        message: "Informe um e-mail válido.",
      },
    };
  }

  // --- Integração real: substituir este bloco ---
  // Exemplo:
  // await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/password-reset`, {
  //   method: "POST",
  //   headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify({ email }),
  // });

  if (process.env.NODE_ENV === "production") {
    return {
      ok: false,
      error: {
        code: "connection_error",
        message:
          "Redefinição de senha ainda não está conectada à API. Contate a equipe ForceIA.",
      },
    };
  }

  await simulateNetwork();

  // Demo: fail@forceia.com simula erro de conexão (apenas desenvolvimento)
  if (email === "fail@forceia.com") {
    return {
      ok: false,
      error: {
        code: "connection_error",
        message:
          "Não foi possível enviar as instruções agora. Tente novamente em instantes.",
      },
    };
  }

  // Sempre sucesso genérico — não revelar existência da conta
  return { ok: true };
}

function simulateNetwork(ms = 1000): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
