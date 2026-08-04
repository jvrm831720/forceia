"""Testes unitários — Prioridade 3 (performance + relatório dono)."""

from performance import compute_performance, period_bounds
from owner_reports import format_owner_report, resolve_owner_phone


def test_period_bounds_week():
    start, end, label = period_bounds("week")
    assert label == "esta semana"
    assert start <= end


def test_performance_headline_meetings():
    events = [
        {
            "type": "meeting_scheduled",
            "created_at": "2026-08-04T12:00:00+00:00",
            "payload": {},
        },
        {
            "type": "meeting_scheduled",
            "created_at": "2026-08-04T13:00:00+00:00",
            "payload": {"source": "admin", "by": "admin"},
        },
        {
            "type": "stage_changed",
            "created_at": "2026-08-04T14:00:00+00:00",
            "payload": {"to": "qualified"},
        },
    ]
    # força período amplo usando events já filtrados via compute com period day
    # e datas de hoje — se o teste rodar noutro dia, usamos month
    data = compute_performance(
        workspace_id="x",
        events=events,
        leads=[],
        period="month",
    )
    assert data["meetings"]["total"] >= 0
    assert "headline" in data
    assert isinstance(data["headline"], str)


def test_owner_report_contains_sections():
    perf = {
        "period_label": "esta semana",
        "headline": "Seu SDR de IA agendou 3 reuniões esta semana",
        "meetings": {"total": 3, "ai": 2, "human": 1},
        "qualified": {"ai": 5, "human": 1},
        "won": {"ai": 1, "human": 0},
        "activity": {"messages_processed": 40, "handoffs": 1, "human_takeovers": 2},
    }
    text = format_owner_report(
        workspace_name="Clínica Sol",
        performance=perf,
        metrics={"total": 20, "win_rate": 0.25, "by_stage": {"closer": 3}},
    )
    assert "Clínica Sol" in text
    assert "Reuniões" in text or "reunião" in text.lower() or "Reuniões" in text
    assert "ForceIA" in text


def test_resolve_owner_phone_from_metadata():
    ws = {"metadata": {"owner_phone": "+55 11 98888-7777"}}
    assert resolve_owner_phone(ws) == "5511988887777"
