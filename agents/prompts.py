"""Carrega prompts dos agentes.

Ordem de precedencia:
1. Override ativo no Supabase (por workspace, se informado)
2. Override global no Supabase
3. Arquivo config/prompts/{agent}.md
4. DEFAULTS embutido
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "config" / "prompts"

DEFAULTS = {
    "sdr": (
        "Voce e o SDR da ForceIA no WhatsApp (Brasil B2B). "
        "Qualifique com BANT, no maximo 1-2 perguntas por mensagem. "
        "Termine com bloco ---META---."
    ),
    "closer": (
        "Voce e o Closer da ForceIA. Avance o fechamento e trate objecoes. "
        "Termine com bloco ---META---."
    ),
    "followup": (
        "Voce reativa leads frios com mensagem curta e de valor. "
        "Termine com bloco ---META---."
    ),
}


def load_prompt_from_file(agent: str) -> str:
    path = PROMPTS_DIR / f"{agent}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return DEFAULTS.get(agent, DEFAULTS["sdr"])


def load_prompt(agent: str, workspace_id: str | None = None) -> str:
    """Carrega prompt com overrides do ciclo de aprendizado."""
    try:
        from db import get_prompt_override

        overridden = get_prompt_override(agent, workspace_id=workspace_id)
        if overridden and len(overridden.strip()) > 40:
            return overridden
    except Exception:
        pass
    return load_prompt_from_file(agent)
