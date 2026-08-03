"""Parsing de payloads da Evolution API."""

from __future__ import annotations

from dataclasses import dataclass

from utils import normalize_phone


@dataclass
class IncomingMessage:
    number: str
    text: str
    instance: str | None = None
    message_id: str | None = None
    from_me: bool = False


def parse_evolution_payload(body: dict) -> IncomingMessage:
    data = body.get("data") or body
    instance = (
        body.get("instance")
        or data.get("instance")
        or (data.get("key") or {}).get("instance")
    )
    key = data.get("key") or {}
    remote_jid = key.get("remoteJid") or data.get("from") or ""
    number = normalize_phone(
        remote_jid.replace("@s.whatsapp.net", "").replace("@g.us", "").replace("+", "")
    )
    message = data.get("message") or {}
    text = (
        message.get("conversation")
        or (message.get("extendedTextMessage") or {}).get("text")
        or data.get("text")
        or ""
    )
    message_id = key.get("id") or data.get("messageId") or data.get("id")
    from_me = bool(key.get("fromMe"))
    return IncomingMessage(
        number=number,
        text=(text or "").strip(),
        instance=instance,
        message_id=message_id,
        from_me=from_me,
    )
