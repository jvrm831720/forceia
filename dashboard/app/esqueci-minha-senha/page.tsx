import type { Metadata } from "next";
import { AuthLayout } from "@/components/auth/auth-layout";
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form";

export const metadata: Metadata = {
  title: "ForceIA · Recuperar senha",
  description: "Recupere o acesso ao Painel Cliente da ForceIA.",
};

export default function EsqueciMinhaSenhaPage() {
  return (
    <AuthLayout>
      <ForgotPasswordForm />
    </AuthLayout>
  );
}
