"""
ForceIA — autenticação JWT do painel admin (hardened).

Fluxo:
  1. POST /api/auth/login  { username, password }  →  { access_token, token_type, expires_in }
  2. Requests autenticados:  Authorization: Bearer <access_token>

Compatibilidade:
  - ADMIN_TOKEN legado ainda é aceito (header X-Admin-Token ou Bearer com o mesmo valor)
    para scripts/CI existentes. Preferir JWT em produção.

Env:
  JWT_SECRET          obrigatório em produção (HS256, ≥32 chars)
  JWT_EXPIRE_MINUTES  default 480 (8h)
  ADMIN_USER          default "admin"
  ADMIN_PASSWORD      senha do operador (política forte)
  ADMIN_TOKEN         token estático legado (opcional; evite em prod)
"""

from __future__ import annotations

import os
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

try:
    from fastapi import Header, HTTPException
except ImportError:  # testes unitários sem FastAPI instalado
    Header = None  # type: ignore

    class HTTPException(Exception):  # type: ignore
        def __init__(self, status_code: int, detail: str = ""):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)

try:
    from pydantic import BaseModel, Field
except ImportError:  # pragma: no cover
    BaseModel = object  # type: ignore

    def Field(*_a, **_k):  # type: ignore
        return None

try:
    import jwt
except ImportError:  # pragma: no cover
    jwt = None  # type: ignore


class LoginIn(BaseModel):  # type: ignore[misc]
    username: str = Field(min_length=1, max_length=128)  # type: ignore[call-arg]
    password: str = Field(min_length=1, max_length=256)  # type: ignore[call-arg]


class TokenOut(BaseModel):  # type: ignore[misc]
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    username: str


MIN_PASSWORD_LENGTH = 12
COMMON_PASSWORDS = frozenset(
    {
        "password",
        "password123",
        "12345678",
        "123456789012",
        "qwerty123456",
        "admin",
        "admin123",
        "admin123456",
        "forceia",
        "forceia123",
        "troque-esta-senha",
        "changeme",
        "changeme123",
        "senha1234567",
        "senha12345678",
        "letmein12345",
        "welcome12345",
    }
)


def validate_password_strength(password: str) -> list[str]:
    errors: list[str] = []
    if password is None:
        return ["senha obrigatoria"]
    if not isinstance(password, str):
        return ["senha invalida"]
    if not password or password.strip() != password:
        if not password.strip():
            errors.append("senha nao pode ser vazia")
        else:
            errors.append("senha nao pode comecar/terminar com espaco")
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"minimo de {MIN_PASSWORD_LENGTH} caracteres")
    if len(password) > 256:
        errors.append("maximo de 256 caracteres")
    if not any(c.islower() for c in password):
        errors.append("precisa de letra minuscula")
    if not any(c.isupper() for c in password):
        errors.append("precisa de letra maiuscula")
    if not any(c.isdigit() for c in password):
        errors.append("precisa de digito")
    if not any(not c.isalnum() and not c.isspace() for c in password):
        errors.append("precisa de simbolo (ex: !@#$%&*)")
    lowered = password.lower().strip()
    if lowered in COMMON_PASSWORDS:
        errors.append("senha comum ou placeholder nao permitida")
    if lowered in {"abcdefghijkl", "abcdefghijk1", "aaaaaaaaaaaa"}:
        errors.append("padrao previsivel")
    return errors


def is_strong_password(password: str) -> bool:
    return not validate_password_strength(password)


def password_policy_enabled() -> bool:
    flag = (os.getenv("FORCEIA_ALLOW_WEAK_PASSWORD") or "").strip().lower()
    return flag not in {"1", "true", "yes", "on"}


def assert_admin_password_policy() -> list[str]:
    pwd = (os.getenv("ADMIN_PASSWORD") or "").strip()
    if not pwd:
        return []
    if not password_policy_enabled():
        return []
    return validate_password_strength(pwd)


def _jwt_secret() -> str:
    secret = (os.getenv("JWT_SECRET") or "").strip()
    if secret:
        return secret
    legacy = (os.getenv("ADMIN_TOKEN") or "").strip()
    if legacy:
        return f"forceia-dev::{legacy}"
    return "forceia-insecure-dev-secret-change-me"


def _expire_minutes() -> int:
    try:
        return max(5, min(int(os.getenv("JWT_EXPIRE_MINUTES", "480")), 60 * 24 * 7))
    except ValueError:
        return 480


def auth_enabled() -> bool:
    if (os.getenv("ADMIN_PASSWORD") or "").strip():
        return True
    if (os.getenv("ADMIN_TOKEN") or "").strip():
        return True
    return False


def verify_password(username: str, password: str) -> bool:
    expected_user = (os.getenv("ADMIN_USER") or "admin").strip()
    expected_pass = (os.getenv("ADMIN_PASSWORD") or "").strip()
    if not expected_pass:
        return False
    if password_policy_enabled() and validate_password_strength(expected_pass):
        return False
    user_ok = secrets.compare_digest(username.strip(), expected_user)
    pass_ok = secrets.compare_digest(password, expected_pass)
    return user_ok and pass_ok


def create_access_token(
    *,
    username: str,
    extra: dict[str, Any] | None = None,
) -> tuple[str, int]:
    if jwt is None:
        raise RuntimeError("Pacote PyJWT nao instalado. pip install PyJWT")
    minutes = _expire_minutes()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": username,
        "role": "admin",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
        "iss": "forceia-admin",
        "type": "access",
        "jti": secrets.token_hex(8),
    }
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, _jwt_secret(), algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token, minutes * 60


def decode_access_token(token: str) -> dict[str, Any]:
    if jwt is None:
        raise HTTPException(status_code=503, detail="PyJWT nao instalado")
    try:
        return jwt.decode(
            token,
            _jwt_secret(),
            algorithms=["HS256"],
            options={"require": ["exp", "sub", "type"]},
            issuer="forceia-admin",
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expirado") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Token invalido") from exc


def _extract_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(None, 1)
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1].strip() or None


def _legacy_token_ok(candidate: str | None) -> bool:
    legacy = (os.getenv("ADMIN_TOKEN") or "").strip()
    if not legacy or not candidate:
        return False
    # Em produção, ADMIN_TOKEN legado pode ser desligado
    if (os.getenv("FORCEIA_DISABLE_LEGACY_TOKEN") or "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        return False
    return secrets.compare_digest(candidate, legacy)


def require_auth(
    authorization: str | None = None,
    x_admin_token: str | None = None,
) -> dict[str, Any]:
    if not auth_enabled():
        raise HTTPException(
            status_code=503,
            detail="Auth desativada: defina ADMIN_PASSWORD (JWT) ou ADMIN_TOKEN",
        )

    bearer = _extract_bearer(authorization)

    if bearer and not _legacy_token_ok(bearer):
        claims = decode_access_token(bearer)
        if claims.get("type") != "access":
            raise HTTPException(status_code=401, detail="Token invalido")
        if claims.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Sem permissao")
        return claims

    if _legacy_token_ok(bearer) or _legacy_token_ok(x_admin_token):
        return {"sub": "legacy", "role": "admin", "type": "legacy"}

    raise HTTPException(status_code=401, detail="Nao autenticado")


def require_token(
    authorization: str | None = None,
    x_admin_token: str | None = None,
) -> dict[str, Any]:
    return require_auth(authorization=authorization, x_admin_token=x_admin_token)


if Header is not None:

    def require_token(  # type: ignore[no-redef]
        authorization: str | None = Header(default=None),
        x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
    ) -> dict[str, Any]:
        return require_auth(authorization=authorization, x_admin_token=x_admin_token)
