"""
ForceIA — utilitários de segurança.

- Rate limit em memória (login / webhook)
- Validação de URL (anti-SSRF) para scrapers
- Checagem de JWT_SECRET em produção
- Headers HTTP de endurecimento
"""

from __future__ import annotations

import ipaddress
import os
import re
import threading
import time
from collections import defaultdict, deque
from typing import Any
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Rate limit (token bucket simples por chave)
# ---------------------------------------------------------------------------

_lock = threading.Lock()
_hits: dict[str, deque[float]] = defaultdict(deque)


def rate_limit_allow(
    key: str,
    *,
    limit: int = 20,
    window_seconds: float = 60.0,
) -> bool:
    """True se a requisição pode seguir; False se excedeu o limite."""
    now = time.monotonic()
    with _lock:
        q = _hits[key]
        while q and now - q[0] > window_seconds:
            q.popleft()
        if len(q) >= limit:
            return False
        q.append(now)
        return True


def client_ip_from_headers(
    *,
    x_forwarded_for: str | None = None,
    x_real_ip: str | None = None,
    fallback: str = "unknown",
) -> str:
    if x_forwarded_for:
        # primeiro hop (cliente original atrás de proxy confiável)
        return x_forwarded_for.split(",")[0].strip() or fallback
    if x_real_ip:
        return x_real_ip.strip() or fallback
    return fallback


# ---------------------------------------------------------------------------
# Anti-SSRF
# ---------------------------------------------------------------------------

_BLOCKED_HOST_SUFFIXES = (
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "tiktok.com",
)

_BLOCKED_HOSTS = frozenset(
    {
        "localhost",
        "metadata.google.internal",
        "metadata",
        "kubernetes",
        "kubernetes.default",
        "kubernetes.default.svc",
    }
)


def _is_private_ip(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def validate_public_http_url(url: str, *,
                             allow_http: bool = False) -> tuple[bool, str]:
    """
    Valida URL para fetch externo (scraper).
    Retorna (ok, motivo_erro).
    """
    if not url or not isinstance(url, str):
        return False, "url vazia"
    url = url.strip()
    if len(url) > 2000:
        return False, "url muito longa"
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "url inválida"

    scheme = (parsed.scheme or "").lower()
    if scheme not in ("https", "http"):
        return False, "apenas http(s) permitido"
    if scheme == "http" and not allow_http:
        # permite http só se FORCEIA_SCRAPE_ALLOW_HTTP=1
        if (os.getenv("FORCEIA_SCRAPE_ALLOW_HTTP") or "").strip().lower() not in (
            "1",
            "true",
            "yes",
        ):
            return False, "apenas https (defina FORCEIA_SCRAPE_ALLOW_HTTP=1 para http)"

    host = (parsed.hostname or "").lower().strip()
    if not host:
        return False, "host ausente"
    if host in _BLOCKED_HOSTS:
        return False, f"host bloqueado: {host}"
    if host.endswith(".local") or host.endswith(".internal") or host.endswith(".localhost"):
        return False, "host local/internal bloqueado"
    for suf in _BLOCKED_HOST_SUFFIXES:
        if host == suf or host.endswith("." + suf):
            return False, f"domínio não suportado: {suf}"

    # IP literal
    if _is_private_ip(host):
        return False, "IP privado/loopback bloqueado (anti-SSRF)"

    # hostname que resolve para privado — checagem best-effort
    try:
        import socket

        infos = socket.getaddrinfo(host, None)
        for info in infos:
            addr = info[4][0]
            if _is_private_ip(addr):
                return False, f"host resolve para IP privado ({addr})"
    except Exception:
        # DNS falhou — deixa o httpx falhar depois; não libera privado conhecido
        pass

    if parsed.username or parsed.password:
        return False, "credenciais na URL não permitidas"

    return True, ""


# ---------------------------------------------------------------------------
# JWT / produção
# ---------------------------------------------------------------------------

_WEAK_JWT = frozenset(
    {
        "forceia-insecure-dev-secret-change-me",
        "secret",
        "changeme",
        "jwt_secret",
        "forceia",
    }
)


def is_production() -> bool:
    env = (os.getenv("FORCEIA_ENV") or os.getenv("ENV") or "").strip().lower()
    return env in ("prod", "production")


def assert_jwt_secret_safe() -> list[str]:
    """Erros se JWT_SECRET fraco em produção ou muito curto."""
    errors: list[str] = []
    secret = (os.getenv("JWT_SECRET") or "").strip()
    if not secret:
        if is_production():
            errors.append("JWT_SECRET obrigatório em produção")
        return errors
    if secret.lower() in _WEAK_JWT or secret.startswith("forceia-dev::"):
        errors.append("JWT_SECRET é um valor de desenvolvimento — troque")
    if len(secret) < 32:
        errors.append("JWT_SECRET deve ter pelo menos 32 caracteres")
    return errors


def security_headers() -> dict[str, str]:
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Cache-Control": "no-store",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        ),
    }
