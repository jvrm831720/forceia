import type { PasswordResetRequest, PasswordResetResult } from "@/types/auth";

/**
 * Solicitação de redefinição de senha.
 *
 * Sempre retorna sucesso genérico para não revelar se o e-mail existe.
 * Substitua o corpo pela integração real (API ForceIA / provedor de auth).
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
  // Exemplo: await fetch("/api/auth/password-reset", { method: "POST", body: JSON.stringify({ email }) })
  await simulateNetwork();

  // Demo: fail@forceia.com simula erro de conexão
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
