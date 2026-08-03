"""Utilitarios puros (sem IO) — faceis de testar."""

from __future__ import annotations

import re


def normalize_phone(phone: str) -> str:
    """Mantem apenas digitos do telefone."""
    return "".join(c for c in (phone or "") if c.isdigit())


_STAGE_TAG_RE = re.compile(
    r"\[(?:QUALIFICADO|QUALIFIED|FECHADO|WON|PERDIDO|LOST|FOLLOW-?UP)\]",
    re.IGNORECASE,
)


def strip_stage_tags(text: str) -> str:
    """Remove tags de controle de estagio antes de enviar ao lead."""
    if not text:
        return text
    cleaned = _STAGE_TAG_RE.sub("", text)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r" *\n *", "\n", cleaned)
    return cleaned.strip()
