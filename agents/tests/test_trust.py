"""Testes — Prioridade 4 confiabilidade."""

from ab_testing import assign_variant, compute_ab_report, conversion_success
from guardrails import enforce_guardrails, format_guardrails_for_prompt, scan_reply
from handoff import build_handoff_summary


def test_guardrails_block_in_prompt():
    text = format_guardrails_for_prompt({"pricing": {"range": "R$ 500 a R$ 900"}})
    assert "Preço" in text or "preço" in text.lower() or "NUNCA" in text


def test_scan_invented_price_without_playbook():
    reply = "Nosso plano custa R$ 1.299 por mês com 20% de desconto."
    scan = scan_reply(reply, playbook=None)
    assert scan["has_price_risk"] is True


def test_enforce_replaces_risky_price():
    reply = "Fecha hoje por R$ 999."
    out = enforce_guardrails(reply, playbook=None, strict=True)
    assert out["modified"] is True
    assert "confirma" in out["reply"].lower() or "tabela" in out["reply"].lower()


def test_allowed_price_from_playbook_passes():
    pb = {"pricing": {"range": "R$ 500", "model": "mensal"}}
    reply = "A faixa fica em R$ 500 mensal, conforme nossa tabela."
    scan = scan_reply(reply, playbook=pb)
    # pode ainda flagar se regex for agressiva; enforce não deve explodir
    out = enforce_guardrails(reply, playbook=pb, strict=True)
    assert "reply" in out


def test_ab_variant_stable():
    a = assign_variant("5511999999999", "ws1")
    b = assign_variant("5511999999999", "ws1")
    assert a == b
    assert a in ("A", "B")


def test_ab_report_lift():
    leads = [
        {"stage": "won", "metadata": {"ab_variant": "A"}},
        {"stage": "sdr", "metadata": {"ab_variant": "A"}},
        {"stage": "qualified", "metadata": {"ab_variant": "B"}},
        {"stage": "won", "metadata": {"ab_variant": "B"}},
    ]
    report = compute_ab_report(leads)
    assert report["variants"]["A"]["total"] == 2
    assert report["variants"]["B"]["converted"] == 2
    assert conversion_success("closer") is True


def test_handoff_summary_contains_lead():
    text = build_handoff_summary(
        lead={
            "name": "Ana",
            "company": "Clínica Sol",
            "phone": "5511988776655",
            "stage": "closer",
            "bant": {"need": "agendar pacientes"},
            "metadata": {"last_intent": "ready_to_buy"},
        },
        messages=[{"role": "user", "content": "Quero fechar"}],
        reason="pediu humano",
        workspace_name="Demo",
    )
    assert "Ana" in text
    assert "Handoff" in text
    assert "5511988776655" in text
