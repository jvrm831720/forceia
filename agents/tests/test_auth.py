"""Testes de autenticação JWT do painel admin."""

from __future__ import annotations

import os

import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def _auth_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret-forceia-jwt-please-change")
    monkeypatch.setenv("ADMIN_USER", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "Admin!ForceIA2026x")
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "60")
    monkeypatch.delenv("ADMIN_TOKEN", raising=False)
    monkeypatch.delenv("FORCEIA_ALLOW_WEAK_PASSWORD", raising=False)
    yield


def test_verify_password_ok():
    from auth import verify_password

    assert verify_password("admin", "Admin!ForceIA2026x") is True
    assert verify_password("admin", "wrong") is False
    assert verify_password("other", "Admin!ForceIA2026x") is False


def test_create_and_decode_token():
    from auth import create_access_token, decode_access_token

    token, expires_in = create_access_token(username="admin")
    assert expires_in == 3600
    claims = decode_access_token(token)
    assert claims["sub"] == "admin"
    assert claims["role"] == "admin"
    assert claims["type"] == "access"


def test_decode_invalid():
    from auth import HTTPException, decode_access_token

    with pytest.raises(HTTPException) as ei:
        decode_access_token("not.a.jwt")
    assert ei.value.status_code == 401


def test_require_auth_jwt(monkeypatch):
    from auth import create_access_token, require_auth

    token, _ = create_access_token(username="admin")
    claims = require_auth(authorization=f"Bearer {token}", x_admin_token=None)
    assert claims["sub"] == "admin"


def test_require_auth_legacy(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "legacy-static-token")
    from auth import require_auth

    claims = require_auth(
        authorization="Bearer legacy-static-token",
        x_admin_token=None,
    )
    assert claims["type"] == "legacy"


def test_auth_enabled(monkeypatch):
    from auth import auth_enabled

    assert auth_enabled() is True
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    monkeypatch.delenv("ADMIN_TOKEN", raising=False)
    assert auth_enabled() is False


def test_password_strength_strong():
    from auth import is_strong_password, validate_password_strength

    assert validate_password_strength("Admin!ForceIA2026x") == []
    assert is_strong_password("Admin!ForceIA2026x") is True


def test_password_strength_weak_cases():
    from auth import validate_password_strength

    assert "minimo de 12 caracteres" in validate_password_strength("Ab1!")
    errs = validate_password_strength("alllowercase1!")
    assert any("maiuscula" in e for e in errs)
    errs = validate_password_strength("ALLUPPERCASE1!")
    assert any("minuscula" in e for e in errs)
    errs = validate_password_strength("NoDigitsHere!!")
    assert any("digito" in e for e in errs)
    errs = validate_password_strength("NoSymbolHere12")
    assert any("simbolo" in e for e in errs)
    errs = validate_password_strength("troque-esta-senha")
    assert any("comum" in e or "placeholder" in e for e in errs)


def test_verify_blocks_weak_configured_password(monkeypatch):
    from auth import verify_password

    monkeypatch.setenv("ADMIN_PASSWORD", "senhafraca")
    assert verify_password("admin", "senhafraca") is False


def test_allow_weak_password_escape_hatch(monkeypatch):
    from auth import assert_admin_password_policy, verify_password

    monkeypatch.setenv("ADMIN_PASSWORD", "senhafraca")
    monkeypatch.setenv("FORCEIA_ALLOW_WEAK_PASSWORD", "1")
    assert assert_admin_password_policy() == []
    assert verify_password("admin", "senhafraca") is True
