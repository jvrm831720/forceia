"""
ForceIA — Playground de simulação.

Testa o SDR/Closer com lead fictício sem gravar no funil real.
Usa o mesmo playbook + prompts do workspace.
"""

from __future__ import annotations

from typing import Any

from intelligence import (
    apply_meta_to_lead_fields,
    bant_score,
    split_reply_and_meta,
    stage_from_meta_or_tags,
)
from state_machine import can_transition, next_agent_for_stage
from utils import strip_control_blocks


def default_fictional_lead(
    *,
    name: str | None = None,
    company: str | None = None,
    stage: str = "sdr",
    persona_note: str | None = None,
) -> dict[str, Any]:
    return {
        "id": None,
        "phone": "playground",
        "name": name or "Lead Demo",
        "company": company or "Empresa Fictícia",
        "email": None,
        "stage": stage or "sdr",
        "bant": {},
        "metadata": {
            "playground": True,
            "persona_note": persona_note or "Lead fictício para teste do agente",
        },
    }


def simulate_turn(
    *,
    workspace: dict,
    user_message: str,
    history: list[dict] | None = None,
    lead: dict | None = None,
    agent: str | None = None,
) -> dict[str, Any]:
    """
    Um turno de conversa no playground.

    Não persiste lead/messages no Supabase.
    Retorna reply visível + meta + lead atualizado (em memória) + history estendido.
    """
    from run_sdr import generate_reply
    from workspace_context import WorkspaceContext

    ws = WorkspaceContext.from_row(workspace)
    lead_state = dict(lead or default_fictional_lead())
    lead_state.setdefault("bant", {})
    lead_state.setdefault("metadata", {})
    lead_state["metadata"]["playground"] = True

    stage = (lead_state.get("stage") or "sdr").lower()
    if agent:
        agent_name = agent.lower()
    elif stage in ("won", "lost"):
        agent_name = "closer" if stage == "won" else "sdr"
    else:
        agent_name = next_agent_for_stage(stage)

    hist = list(history or [])
    raw = generate_reply(
        ws,
        agent_name,
        hist,
        user_message,
        lead=lead_state,
    )
    visible, meta = split_reply_and_meta(raw)
    reply = strip_control_blocks(visible)

    field_updates = apply_meta_to_lead_fields(lead_state, meta, user_message)
    for k, v in field_updates.items():
        if k == "metadata":
            merged_meta = dict(lead_state.get("metadata") or {})
            merged_meta.update(v or {})
            lead_state["metadata"] = merged_meta
        else:
            lead_state[k] = v

    new_stage = stage_from_meta_or_tags(raw, meta, stage, can_transition)
    lead_state["stage"] = new_stage

    hist.append({"role": "user", "content": user_message})
    hist.append({"role": "assistant", "content": reply, "agent": agent_name})

    return {
        "reply": reply,
        "agent": agent_name,
        "meta": meta,
        "lead": {
            "name": lead_state.get("name"),
            "company": lead_state.get("company"),
            "email": lead_state.get("email"),
            "stage": lead_state.get("stage"),
            "bant": lead_state.get("bant") or {},
            "bant_score": bant_score(lead_state.get("bant")),
            "metadata": {
                k: v
                for k, v in (lead_state.get("metadata") or {}).items()
                if k in ("playground", "last_intent", "persona_note", "objections", "buying_intent")
            },
        },
        "history": hist[-40:],
        "playground": True,
    }
