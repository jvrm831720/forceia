from utils import env_flag, normalize_phone, strip_stage_tags


def test_normalize_phone():
    assert normalize_phone("+55 (11) 99999-8888") == "5511999998888"
    assert normalize_phone("") == ""
    assert normalize_phone(None) == ""  # type: ignore[arg-type]
    assert normalize_phone("abc123") == "123"


def test_strip_stage_tags():
    assert strip_stage_tags("Ok [QUALIFICADO] vamos agendar?") == "Ok vamos agendar?"
    assert strip_stage_tags("[FECHADO] parabens") == "parabens"
    assert strip_stage_tags("nada aqui") == "nada aqui"
    assert strip_stage_tags("") == ""


def test_strip_multiple_tags_and_case():
    assert strip_stage_tags("a [qualificado] b [followup] c") == "a b c"


def test_env_flag():
    assert env_flag("true") is True
    assert env_flag("1") is True
    assert env_flag("sim") is True
    assert env_flag("no") is False
    assert env_flag(None, default=True) is True
    assert env_flag(None) is False
