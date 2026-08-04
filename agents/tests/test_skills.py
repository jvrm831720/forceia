"""Testes — skills de elite ForceIA."""

from skills.icp_fit import compute_icp_fit
from skills.personalization import build_personalization_brief
from skills.pipeline_health import score_pipeline_lead
from skills.pre_call import build_pre_call_brief
from skills.revival import score_revival


def test_icp_fit_senior_title():
    lead = {
        "name": "Ana",
        "company": "Clínica Sol",
        "stage": "sdr",
        "bant": {"need": "agenda"},
        "metadata": {"enrichment": {"title": "CEO"}, "buying_intent": "ready_to_buy"},
    }
    playbook = {
        "icp": {"roles": ["CEO", "Diretor"], "industries": ["saúde"]},
        "persona": {"buyer_titles": ["CEO"], "pains": ["agenda lotada"]},
    }
    info = compute_icp_fit(lead, playbook)
    assert info["score"] >= 60
    assert info["grade"] in ("A", "B", "C")


def test_personalization_has_opener():
    brief = build_personalization_brief(
        {"name": "Ana Silva", "company": "Clínica Sol", "metadata": {"enrichment": {"title": "Dona"}}},
        {"persona": {"pains": ["no-show de pacientes"]}, "value_proposition": "reduzir faltas"},
    )
    assert brief["angles"]
    assert brief["recommended"]["opener"]


def test_pre_call_brief():
    b = build_pre_call_brief(
        {
            "name": "Ana",
            "company": "Sol",
            "stage": "closer",
            "bant": {"need": "automação", "budget": "5k"},
            "metadata": {},
        },
        {"product_summary": "WhatsApp sales AI", "cases": [{"title": "Clínica X", "result": "+30%"}]},
        messages=[{"role": "user", "content": "Quero fechar"}],
    )
    assert "Ana" in b["executive_summary"]
    assert b["talking_points"]


def test_revival_high_for_budget():
    r = score_revival(
        {
            "name": "João",
            "company": "Acme",
            "stage": "lost",
            "bant": {"need": "sim"},
            "metadata": {"lost_reason": "budget timing"},
        }
    )
    assert r["priority"] in ("High", "Medium")
    assert r["suggested_opener"]


def test_pipeline_health_tiers():
    hot = score_pipeline_lead(
        {
            "stage": "closer",
            "name": "A",
            "company": "B",
            "last_message_at": "2026-08-04T12:00:00+00:00",
            "bant": {"need": "x", "authority": "y", "budget": "z"},
            "metadata": {},
        }
    )
    assert hot["health"] >= 5
    assert hot["tier"] in ("Hot", "Warm", "At Risk", "Cold")
