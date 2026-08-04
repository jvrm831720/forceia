"""Testes de segurança."""

from security import rate_limit_allow, validate_public_http_url


def test_block_localhost():
    ok, reason = validate_public_http_url("http://127.0.0.1/secret")
    assert ok is False
    assert "privado" in reason.lower() or "loopback" in reason.lower() or "http" in reason.lower()


def test_block_metadata():
    ok, _ = validate_public_http_url("http://169.254.169.254/latest/meta-data/")
    assert ok is False


def test_block_linkedin():
    ok, _ = validate_public_http_url("https://www.linkedin.com/jobs/view/1")
    assert ok is False


def test_allow_https_public():
    ok, reason = validate_public_http_url("https://boards.greenhouse.io/acme")
    assert ok is True, reason


def test_rate_limit_trips():
    key = "test:unit:rl"
    # limpa indiretamente usando chave única e limite baixo
    allowed = 0
    for _ in range(5):
        if rate_limit_allow(key, limit=3, window_seconds=60):
            allowed += 1
    assert allowed == 3
