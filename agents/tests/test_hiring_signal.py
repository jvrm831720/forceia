"""Testes — hiring signal prospector."""

from skills.hiring_signal import analyze_hiring_signal, hiring_signal_from_lead


def test_strong_first_sdr():
    r = analyze_hiring_signal(
        role="Sales Development Representative (First Hire)",
        company="CloudMetrics",
        jd_snippet="We're looking for our first SDR to build the outbound engine from the ground up.",
        decision_maker_name="Alex Rivera",
        playbook={"product_summary": "WhatsApp sales AI", "value_proposition": "pipeline no WhatsApp"},
    )
    assert r["signal_strength"] == "Strong"
    assert r["priority"] == "HIGH"
    assert "Alex" in r["suggested_opener"] or "CloudMetrics" in r["suggested_opener"]


def test_from_lead_metadata():
    lead = {
        "name": "Ana",
        "company": "Clínica Sol",
        "metadata": {
            "hiring_signal": {
                "role": "Closer",
                "jd_snippet": "Estamos expandindo o time comercial e contratando closer.",
                "company": "Clínica Sol",
            }
        },
    }
    info = hiring_signal_from_lead(lead, {"product_summary": "ForceIA"})
    assert info is not None
    assert info["signal_strength"] in ("Strong", "Medium", "Soft")
