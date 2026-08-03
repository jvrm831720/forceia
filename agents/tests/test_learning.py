"""Testes puros do ciclo de aprendizado (sem OpenAI/Supabase)."""

from learning import ensure_meta_protocol, parse_analyst_json, _transcript


def test_parse_analyst_json_plain():
    prompt = "x" * 100
    raw = (
        '{"summary":"ok","insights":[],'
        f'"suggestions":[{{"agent":"sdr","suggested_prompt":"{prompt}"}}]'
        "}"
    )
    data = parse_analyst_json(raw)
    assert data["summary"] == "ok"
    assert data["suggestions"][0]["agent"] == "sdr"


def test_parse_analyst_json_fenced():
    raw = '```json\n{"summary":"y","insights":[],"suggestions":[]}\n```'
    data = parse_analyst_json(raw)
    assert data["summary"] == "y"


def test_parse_analyst_json_invalid():
    data = parse_analyst_json("nao e json")
    assert data["suggestions"] == []


def test_ensure_meta_protocol_appends():
    p = ensure_meta_protocol("# Prompt sem meta")
    assert "---META---" in p


def test_ensure_meta_protocol_keeps_existing():
    base = "Ola\n---META---\n{}"
    assert ensure_meta_protocol(base) == base


def test_transcript_truncates():
    msgs = [{"role": "user", "content": "a" * 5000}]
    t = _transcript(msgs, max_chars=200)
    assert len(t) <= 200
    assert "cortado" in t
