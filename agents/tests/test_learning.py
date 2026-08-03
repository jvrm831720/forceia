"""Testes puros do ciclo de aprendizado STaR+SPIN (sem OpenAI/Supabase)."""

from learning import (
    _transcript,
    build_preference_pairs,
    ensure_meta_protocol,
    export_preference_dataset,
    parse_analyst_json,
)


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


def test_build_preference_pairs_spin_format():
    won = [
        {
            "lead_id": "w1",
            "transcript": "assistant: vamos fechar o plano completo",
            "agent": "closer",
            "bant": {"need": "SDR"},
        }
    ]
    lost = [
        {
            "lead_id": "l1",
            "transcript": "assistant: ainda tem interesse?",
            "agent": "sdr",
            "bant": {},
        }
    ]
    pairs = build_preference_pairs(won, lost, max_pairs=5)
    assert len(pairs) == 1
    assert pairs[0]["real"]["meta"]["outcome"] == "won"
    assert pairs[0]["generated"]["meta"]["outcome"] == "lost"
    assert "fechar" in pairs[0]["real"]["content"]


def test_export_preference_dataset_hf_shape():
    pairs = build_preference_pairs(
        [{"transcript": "won text", "agent": "sdr", "bant": {}, "lead_id": "1"}],
        [{"transcript": "lost text", "agent": "sdr", "bant": {}, "lead_id": "2"}],
    )
    ds = export_preference_dataset(pairs)
    assert len(ds) == 1
    assert ds[0]["real"][1]["role"] == "assistant"
    assert ds[0]["generated"][1]["content"] == "lost text"
    assert ds[0]["meta"]["real_outcome"] == "won"
