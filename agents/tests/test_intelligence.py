"""Testes da camada de inteligencia (sem OpenAI/Supabase)."""

from intelligence import (
    apply_meta_to_lead_fields,
    bant_score,
    build_lead_context,
    extract_contact_hints,
    is_bant_qualified,
    merge_bant,
    split_reply_and_meta,
    stage_from_meta_or_tags,
)
from state_machine import can_transition
from utils import strip_control_blocks


def test_split_reply_and_meta():
    raw = (
        "Otimo, vamos agendar amanha as 10h.\n\n"
        "---META---\n"
        '{"stage":"qualified","bant":{"need":"leads frios","authority":"decisor","budget":"sim","timeline":"30 dias","score":75}}'
    )
    visible, meta = split_reply_and_meta(raw)
    assert "META" not in visible
    assert "agendar" in visible.lower()
    assert meta["stage"] == "qualified"
    assert meta["bant"]["need"] == "leads frios"


def test_split_meta_with_code_fence():
    raw = 'Oi!\n---META---\n```json\n{"stage":"sdr","bant":{"need":"x"}}\n```'
    visible, meta = split_reply_and_meta(raw)
    assert visible == "Oi!"
    assert meta["bant"]["need"] == "x"


def test_strip_control_blocks_removes_meta_and_tags():
    raw = "Negocio fechado [FECHADO]\n---META---\n{\"stage\":\"won\"}"
    out = strip_control_blocks(raw)
    assert "META" not in out
    assert "[" not in out
    assert "Negocio fechado" in out


def test_bant_score_and_qualify():
    bant = {
        "need": "SDR caro demais",
        "authority": "CEO",
        "budget": "ate 5k",
        "timeline": "este mes",
    }
    assert bant_score(bant) >= 60
    assert is_bant_qualified(bant)
    assert not is_bant_qualified({"need": "talvez"})


def test_merge_bant_keeps_previous():
    old = {"need": "leads", "budget": ""}
    new = {"budget": "sim", "timeline": "15 dias"}
    m = merge_bant(old, new)
    assert m["need"] == "leads"
    assert m["budget"] == "sim"
    assert m["timeline"] == "15 dias"


def test_stage_from_meta():
    assert (
        stage_from_meta_or_tags("", {"stage": "qualified"}, "sdr", can_transition)
        == "qualified"
    )
    assert (
        stage_from_meta_or_tags("ok [FECHADO]", {}, "closer", can_transition) == "won"
    )
    assert stage_from_meta_or_tags("oi", {}, "sdr", can_transition) == "sdr"


def test_extract_contact_hints():
    text = "Oi, meu nome e Maria Silva, trabalho na Acme Tech, email maria@acme.com.br"
    h = extract_contact_hints(text)
    assert h.get("email") == "maria@acme.com.br"
    assert "Maria" in (h.get("name") or "")
    assert "Acme" in (h.get("company") or "")


def test_apply_meta_to_lead_fields():
    lead = {"name": None, "bant": {}, "metadata": {}}
    meta = {
        "name": "Joao",
        "bant": {"need": "automacao WhatsApp"},
        "objection": "preco",
        "intent": "quer demo",
    }
    upd = apply_meta_to_lead_fields(lead, meta, "sou o Joao")
    assert upd["name"] == "Joao"
    assert upd["bant"]["need"] == "automacao WhatsApp"
    assert "preco" in upd["metadata"]["objections"]


def test_build_lead_context_includes_bant():
    lead = {
        "stage": "sdr",
        "name": "Ana",
        "company": "Beta",
        "bant": {"need": "follow-up", "score": 40},
        "metadata": {},
    }
    ctx = build_lead_context(lead, workspace_name="ForceIA")
    assert "Ana" in ctx
    assert "follow-up" in ctx
    assert "sdr" in ctx
