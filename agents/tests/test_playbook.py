"""Testes do playbook por workspace (sem Supabase/OpenAI)."""

from intelligence import build_system_prompt
from playbook import (
    EMPTY_PLAYBOOK,
    extract_playbook_from_workspace,
    format_playbook_for_prompt,
    is_playbook_empty,
    normalize_playbook,
    playbook_completeness,
)


def test_normalize_partial():
    n = normalize_playbook(
        {
            "company_name": "  Acme  ",
            "icp": {"industries": "SaaS, Saúde", "roles": ["CEO"]},
            "pricing": {"range": "R$ 1k-3k"},
            "cases": [{"title": "Cliente X", "result": "+30%"}],
        }
    )
    assert n["company_name"] == "Acme"
    assert "SaaS" in n["icp"]["industries"]
    assert n["icp"]["roles"] == ["CEO"]
    assert n["pricing"]["range"] == "R$ 1k-3k"
    assert n["cases"][0]["title"] == "Cliente X"


def test_empty_playbook():
    assert is_playbook_empty(None)
    assert is_playbook_empty({})
    assert is_playbook_empty(EMPTY_PLAYBOOK)
    assert not is_playbook_empty({"company_name": "X", "product_summary": "produto longo o suficiente"})


def test_format_includes_sections():
    pb = normalize_playbook(
        {
            "company_name": "ForceIA Demo",
            "product_summary": "Agentes de vendas no WhatsApp 24h",
            "value_proposition": "Melhor SDR sem headcount",
            "icp": {"industries": ["SaaS"], "disqualifiers": ["estudante"]},
            "pricing": {"range": "R$ 997+"},
            "objections": [{"objection": "caro", "response": "vs 1 SDR pleno"}],
        }
    )
    text = format_playbook_for_prompt(pb)
    assert "ForceIA Demo" in text
    assert "WhatsApp" in text
    assert "SaaS" in text
    assert "estudante" in text
    assert "R$ 997" in text
    assert "caro" in text


def test_format_empty_returns_blank():
    assert format_playbook_for_prompt({}) == ""
    assert format_playbook_for_prompt(None) == ""


def test_completeness_score():
    empty = playbook_completeness({})
    assert empty["score"] == 0
    assert empty["ready"] is False

    rich = playbook_completeness(
        {
            "company_name": "Acme",
            "product_summary": "Plataforma completa de vendas com agentes IA no WhatsApp",
            "value_proposition": "Triplique reuniões sem contratar SDR",
            "icp": {"industries": ["B2B"], "roles": ["CEO"]},
            "persona": {"pains": ["leads frios"]},
            "pricing": {"model": "mensal", "range": "1-5k"},
            "cases": [{"title": "A", "result": "+20%"}],
            "objections": [{"objection": "preço", "response": "ROI"}],
        }
    )
    assert rich["score"] >= 50
    assert rich["ready"] is True


def test_extract_from_column_and_metadata():
    row_col = {"playbook": {"company_name": "Col"}}
    assert extract_playbook_from_workspace(row_col)["company_name"] == "Col"

    row_meta = {"metadata": {"playbook": {"company_name": "Meta"}}}
    assert extract_playbook_from_workspace(row_meta)["company_name"] == "Meta"


def test_system_prompt_injects_playbook():
    lead = {"stage": "sdr", "bant": {}, "metadata": {}}
    pb = {
        "company_name": "Clinica Sol",
        "product_summary": "Agendamento inteligente para clinicas odontologicas",
        "pricing": {"range": "R$ 490/mes"},
    }
    sys = build_system_prompt("Voce e o SDR.", lead, "Clinica Sol", playbook=pb)
    assert "Playbook do cliente" in sys
    assert "Clinica Sol" in sys
    assert "R$ 490" in sys
    assert "---META---" in sys
    assert "Contexto deste lead" in sys
