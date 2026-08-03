"""ForceIA - Utilitarios puros (sem dependencias externas)."""

from __future__ import annotations

import re

from intelligence import META_MARKER, split_reply_and_meta

_STAGE_TAG_RE = re.compile(
    r"\[(?:QUALIFICADO|QUALIFIED|FECHADO|WON|PERDIDO|LOST|FOLLOW-?UP)\]",
    re.IGNORECASE,
)


def normalize_phone(phone: str | None) -> str:
    """Mantem apenas digitos de um numero de telefone."""
    return "".join(c for c in (phone or "") if c.isdigit())


def strip_stage_tags(text: str) -> str:
    """Remove tags de controle ([QUALIFICADO], [FECHADO]...) do texto."""
    if not text:
        return text
    cleaned = _STAGE_TAG_RE.sub("", text)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r" *\n *", "\n", cleaned)
    return cleaned.strip()


def strip_control_blocks(text: str) -> str:
    """Remove ---META--- e tags de estagio antes de enviar ao lead."""
    if not text:
        return text
    if META_MARKER in text:
        visible, _ = split_reply_and_meta(text)
        text = visible
    return strip_stage_tags(text)


def env_flag(value: str | None, default: bool = False) -> bool:
    """Interpreta uma variavel de ambiente como booleano."""
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on", "sim")
