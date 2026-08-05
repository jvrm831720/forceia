import Link from "next/link";

export function AuthFooter({
  helpHref = "mailto:suporte@forceia.com",
}: {
  helpHref?: string;
}) {
  return (
    <p className="text-center text-[12px] leading-relaxed text-ink-soft">
      Precisa de ajuda?{" "}
      <Link
        href={helpHref}
        className="font-medium text-ink-muted underline-offset-2 transition hover:text-brand hover:underline"
      >
        Fale com o suporte
      </Link>
    </p>
  );
}
