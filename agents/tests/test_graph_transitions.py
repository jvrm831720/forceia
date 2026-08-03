"""Testes das regras de funil usadas pelo grafo (sem LangGraph/OpenAI)."""

from state_machine import STAGES, can_transition, next_agent_for_stage


def test_funnel_stages():
    assert set(STAGES) == {"sdr", "qualified", "closer", "followup", "won", "lost"}


def test_happy_path_transitions():
    assert can_transition("sdr", "qualified")
    assert can_transition("qualified", "closer")
    assert can_transition("closer", "won")


def test_side_paths():
    assert can_transition("sdr", "followup")
    assert can_transition("sdr", "lost")
    assert can_transition("followup", "closer")
    assert can_transition("lost", "sdr")


def test_terminal_won():
    assert not can_transition("won", "sdr")
    assert not can_transition("won", "closer")


def test_agent_mapping_matches_graph():
    assert next_agent_for_stage("sdr") == "sdr"
    assert next_agent_for_stage("qualified") == "closer"
    assert next_agent_for_stage("closer") == "closer"
    assert next_agent_for_stage("followup") == "followup"
