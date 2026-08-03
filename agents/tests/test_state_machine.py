from state_machine import (
    STAGES,
    can_transition,
    detect_stage_from_reply,
    next_agent_for_stage,
)


def test_stages_defined():
    assert set(STAGES) == {"sdr", "qualified", "closer", "followup", "won", "lost"}


def test_next_agent():
    assert next_agent_for_stage("sdr") == "sdr"
    assert next_agent_for_stage("qualified") == "closer"
    assert next_agent_for_stage("closer") == "closer"
    assert next_agent_for_stage("followup") == "followup"
    assert next_agent_for_stage("won") == "closer"  # pos-venda / suporte leve


def test_transitions():
    assert can_transition("sdr", "qualified")
    assert can_transition("qualified", "closer")
    assert can_transition("closer", "won")
    assert not can_transition("won", "sdr")  # terminal
    assert not can_transition("sdr", "won")  # pulo invalido
    assert not can_transition("inexistente", "sdr")


def test_detect_stage_qualified():
    assert detect_stage_from_reply("Legal! [QUALIFICADO]", "sdr") == "qualified"
    assert detect_stage_from_reply("Legal! [QUALIFIED]", "sdr") == "qualified"


def test_detect_stage_won_lost_followup():
    assert detect_stage_from_reply("[FECHADO]", "closer") == "won"
    assert detect_stage_from_reply("[PERDIDO]", "closer") == "lost"
    assert detect_stage_from_reply("[FOLLOWUP]", "sdr") == "followup"


def test_detect_stage_no_tag_keeps_current():
    assert detect_stage_from_reply("sem tag aqui", "closer") == "closer"


def test_detect_stage_respects_invalid_transition():
    # won e terminal: nao deve mudar
    assert detect_stage_from_reply("[QUALIFICADO]", "won") == "won"
