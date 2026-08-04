"""Testes das actions de integração (sem Composio real)."""

from __future__ import annotations

from unittest.mock import patch

from integrations.actions import _extract_meeting, _intent_is_schedule, run_agent_actions
from integrations.tools.calendar import _parse_start


def test_intent_schedule_variants():
    assert _intent_is_schedule({"intent": "schedule"})
    assert _intent_is_schedule({"intent": "agendar"})
    assert _intent_is_schedule({"meeting": {"start": "2026-08-05T15:00:00-03:00"}})
    assert not _intent_is_schedule({"intent": "qualify"})


def test_extract_meeting():
    meta = {
        "intent": "schedule",
        "meeting": {
            "title": "Demo ForceIA",
            "start": "2026-08-05T15:00:00-03:00",
            "duration_minutes": 45,
        },
        "email": "lead@acme.com",
    }
    lead = {"name": "Ana", "email": "lead@acme.com"}
    m = _extract_meeting(meta, lead)
    assert m is not None
    assert m["title"] == "Demo ForceIA"
    assert m["duration_minutes"] == 45
    assert m["attendee_email"] == "lead@acme.com"


def test_parse_start_naive_br():
    dt = _parse_start("2026-08-05T15:00:00", "America/Sao_Paulo")
    assert dt.hour == 15
    assert dt.tzinfo is not None


def test_run_actions_composio_disabled_schedules_pending(monkeypatch):
    monkeypatch.setenv("FORCEIA_COMPOSIO", "0")
    meta = {
        "intent": "schedule",
        "meeting": {"start": "2026-08-05T15:00:00-03:00", "title": "Demo"},
    }
    out = run_agent_actions(
        workspace_id="ws-1",
        agent="closer",
        stage="closer",
        meta=meta,
        lead={"name": "Bob", "phone": "5511999"},
    )
    assert out["lead_metadata"].get("meeting_pending")
    assert any(a["type"] == "schedule_meeting" for a in out["actions"])


def test_run_actions_calendar_success_adds_suffix():
    meta = {
        "intent": "schedule",
        "meeting": {"start": "2026-08-05T15:00:00-03:00", "title": "Demo"},
    }
    fake = {
        "success": True,
        "start": "2026-08-05T15:00:00-03:00",
        "end": "2026-08-05T15:30:00-03:00",
        "event_id": "evt_1",
        "html_link": "https://cal.example/e/1",
        "toolkit": "googlecalendar",
    }
    with patch("integrations.tools.calendar.schedule_meeting", return_value=fake):
        out = run_agent_actions(
            workspace_id="ws-1",
            agent="closer",
            stage="closer",
            meta=meta,
            lead={"name": "Ana"},
        )
    assert out["reply_suffix"] and "confirmada" in out["reply_suffix"].lower()
    assert out["lead_metadata"]["last_meeting"]["event_id"] == "evt_1"


def test_handoff_triggers_notify():
    meta = {"handoff": True, "notes": "quer falar com humano"}
    with patch(
        "integrations.tools.notify.notify_handoff",
        return_value={"success": True, "channel": "#vendas"},
    ) as mock_n:
        out = run_agent_actions(
            workspace_id="ws-1",
            agent="closer",
            stage="closer",
            meta=meta,
            lead={"phone": "5511", "name": "Ana"},
        )
    mock_n.assert_called_once()
    assert out["lead_metadata"].get("handoff_notified") is True
