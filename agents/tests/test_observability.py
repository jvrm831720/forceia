"""Testes do wrapper Langfuse (no-op sem chaves)."""

import os

from observability import TurnTrace, enabled, get_client, start_turn_trace


def test_disabled_without_keys(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    # reset singleton
    import observability as obs

    obs._client = None
    obs._init_attempted = False
    assert enabled() is False
    assert get_client() is None


def test_start_turn_noop_without_keys(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    import observability as obs

    obs._client = None
    obs._init_attempted = False
    tr = start_turn_trace(
        workspace_id="w1",
        workspace_slug="demo",
        phone="5511",
        user_message="oi",
    )
    assert isinstance(tr, TurnTrace)
    assert tr._trace is None
    # no-op methods must not raise
    tr.generation(name="x", model="m", input="i", output="o")
    tr.event("e", foo=1)
    with tr.span("s", a=1):
        pass
    tr.end(output={"ok": True})


def test_enabled_flag_off(monkeypatch):
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk")
    monkeypatch.setenv("LANGFUSE_ENABLED", "0")
    import observability as obs

    obs._client = None
    obs._init_attempted = False
    assert enabled() is False
