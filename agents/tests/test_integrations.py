"""Testes da camada de integrações (Fase 0 + 1) — sem API Composio real."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from integrations.base import IntegrationStatus, ToolkitInfo
from integrations.registry import get_workspace_integrations, toolkit_catalog
from integrations import composio_client as cc


def test_toolkit_catalog_filter():
    all_tk = toolkit_catalog()
    assert any(t.slug == "googlecalendar" for t in all_tk)
    filtered = toolkit_catalog(only_slugs=["gmail", "slack"])
    slugs = {t.slug for t in filtered}
    assert slugs == {"gmail", "slack"}


def test_get_workspace_integrations_disabled():
    available = [
        ToolkitInfo(slug="gmail", name="Gmail", category="email", priority="P0"),
    ]
    rows = get_workspace_integrations(
        available=available,
        connected=[],
        provider_enabled=False,
    )
    assert len(rows) == 1
    assert rows[0]["status"] == IntegrationStatus.DISABLED.value


def test_get_workspace_integrations_connected():
    from integrations.base import ConnectedAccount

    available = toolkit_catalog(only_slugs=["gmail", "slack"])
    connected = [
        ConnectedAccount(
            id="ca_1",
            toolkit="gmail",
            status=IntegrationStatus.CONNECTED,
            display_name="ops@acme.com",
        )
    ]
    rows = get_workspace_integrations(
        available=available,
        connected=connected,
        provider_enabled=True,
    )
    by = {r["slug"]: r for r in rows}
    assert by["gmail"]["status"] == "connected"
    assert by["gmail"]["connection_id"] == "ca_1"
    assert by["slack"]["status"] == "disconnected"


def test_is_composio_enabled_off(monkeypatch):
    monkeypatch.setenv("FORCEIA_COMPOSIO", "0")
    monkeypatch.setenv("COMPOSIO_API_KEY", "sk-test")
    assert cc.is_composio_enabled() is False


def test_is_composio_enabled_on_with_key(monkeypatch):
    monkeypatch.setenv("FORCEIA_COMPOSIO", "1")
    monkeypatch.setenv("COMPOSIO_API_KEY", "sk-test")
    assert cc.is_composio_enabled() is True


def test_is_composio_enabled_default_no_key(monkeypatch):
    monkeypatch.delenv("FORCEIA_COMPOSIO", raising=False)
    monkeypatch.delenv("COMPOSIO_API_KEY", raising=False)
    assert cc.is_composio_enabled() is False


def test_list_available_toolkits_from_env(monkeypatch):
    monkeypatch.setenv("FORCEIA_COMPOSIO_TOOLKITS", "gmail,slack")
    tks = cc.list_available_toolkits()
    assert {t.slug for t in tks} == {"gmail", "slack"}


def test_authorize_disabled(monkeypatch):
    monkeypatch.setenv("FORCEIA_COMPOSIO", "0")
    result = cc.authorize("ws-1", "gmail")
    assert result.status == IntegrationStatus.DISABLED


def test_authorize_outside_allowlist(monkeypatch):
    monkeypatch.setenv("FORCEIA_COMPOSIO", "1")
    monkeypatch.setenv("COMPOSIO_API_KEY", "sk-test")
    monkeypatch.setenv("FORCEIA_COMPOSIO_TOOLKITS", "gmail")
    result = cc.authorize("ws-1", "not-a-real-toolkit")
    assert result.status == IntegrationStatus.ERROR
    assert "allowlist" in (result.message or "").lower()


def test_execute_tool_disabled(monkeypatch):
    monkeypatch.setenv("FORCEIA_COMPOSIO", "0")
    out = cc.execute_tool("ws-1", "GMAIL_SEND_EMAIL", {"to": "a@b.com"})
    assert out["success"] is False
    assert out["error"] == "composio_disabled"


def test_get_or_create_session_creates(monkeypatch):
    monkeypatch.setenv("FORCEIA_COMPOSIO", "1")
    monkeypatch.setenv("COMPOSIO_API_KEY", "sk-test")
    monkeypatch.setenv("FORCEIA_COMPOSIO_TOOLKITS", "gmail")

    fake_session = MagicMock()
    fake_session.session_id = "sess_abc"

    fake_client = MagicMock()
    fake_client.create.return_value = fake_session

    with (
        patch.object(cc, "_client", return_value=fake_client),
        patch.object(cc, "_get_workspace_meta", return_value={}),
        patch.object(cc, "_set_workspace_meta", return_value={"composio_session_id": "sess_abc"}) as set_meta,
    ):
        sid = cc.get_or_create_session("ws-uuid-1")
    assert sid == "sess_abc"
    fake_client.create.assert_called_once()
    assert set_meta.called


def test_provider_protocol():
    p = cc.get_provider()
    assert p.name == "composio"
    assert hasattr(p, "list_toolkits")
    assert hasattr(p, "authorize")
