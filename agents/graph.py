"""
ForceIA LangGraph — carrega implementação P0 de main e aplica overlay P1.
"""
from __future__ import annotations

import os
import urllib.request

_MAIN_GRAPH_URL = os.getenv(
    "FORCEIA_GRAPH_SOURCE_URL",
    "https://raw.githubusercontent.com/jvrm831720/forceia/main/agents/graph.py",
)


def _load_base() -> str:
    with urllib.request.urlopen(_MAIN_GRAPH_URL, timeout=30) as resp:
        return resp.read().decode("utf-8")


_src = _load_base()
exec(compile(_src, "graph_base_from_main.py", "exec"), globals())

# --- P1 overlay (intent routing, turn policy, objection handoff) ---
_orig_prepare = _node_prepare  # type: ignore[name-defined]
_orig_parse = _node_parse  # type: ignore[name-defined]


def _node_prepare(state):  # type: ignore[no-redef]
    out = _orig_prepare(state)
    try:
        from p1_hooks import route_agent_by_intent

        agent = route_agent_by_intent(
            out.get("stage") or "sdr",
            out.get("agent") or "sdr",
            out.get("intent_info") or {},
            out.get("score_info") or {},
        )
        out["agent"] = agent
    except Exception:
        pass
    return out


def _node_parse(state):  # type: ignore[no-redef]
    result = _orig_parse(state)
    try:
        from p1_hooks import (
            apply_turn_policy_to_reply,
            maybe_set_handoff_from_objections,
            route_stage_by_intent,
        )

        reply, ev = apply_turn_policy_to_reply(
            result.get("visible_reply") or "",
            state.get("stage") or "sdr",
            state.get("agent") or "sdr",
        )
        result["visible_reply"] = reply
        events = list(result.get("events") or [])
        events.extend(ev)

        meta, ho = maybe_set_handoff_from_objections(
            result.get("lead") or {},
            result.get("meta") or {},
        )
        result["meta"] = meta
        events.extend(ho)
        if meta.get("handoff"):
            r = result.get("visible_reply") or ""
            if "vou te conectar" not in r.lower() and "humano" not in r.lower():
                result["visible_reply"] = (
                    (r + "\n\n" if r else "")
                    + "Vou acionar alguém do time para te atender em seguida, combinado?"
                ).strip()

        result["new_stage"] = route_stage_by_intent(
            state.get("stage") or "sdr",
            result.get("new_stage") or state.get("stage") or "sdr",
            result.get("intent_info") or {},
            result.get("score_info") or {},
            can_transition,  # type: ignore[name-defined]
        )
        result["events"] = events
    except Exception:
        pass
    return result


# Rebuild compiled graph with patched nodes
_compiled = None  # type: ignore[misc]


def get_compiled_graph():  # type: ignore[no-redef]
    global _compiled
    if _compiled is None:
        if not _langgraph_available():  # type: ignore[name-defined]
            raise RuntimeError("langgraph nao instalado. pip install 'langgraph>=0.2.0'")
        _compiled = build_sales_graph(checkpointer=_default_checkpointer())  # type: ignore[name-defined]
    return _compiled
