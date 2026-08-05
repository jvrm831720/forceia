"""
ForceIA LangGraph — carrega implementação P0 (feat/p0-langgraph-wire)
e aplica overlays P1 (turn policy / intent) + P2 (closer tool registry).
"""
from __future__ import annotations

import os
import urllib.request

# Base P0 vive na branch feat/p0 (main não pode auto-referenciar o loader)
_BASE_GRAPH_URL = os.getenv(
    "FORCEIA_GRAPH_SOURCE_URL",
    "https://raw.githubusercontent.com/jvrm831720/forceia/feat/p0-langgraph-wire/agents/graph.py",
)


def _load_base() -> str:
    with urllib.request.urlopen(_BASE_GRAPH_URL, timeout=30) as resp:
        return resp.read().decode("utf-8")


_src = _load_base()
exec(compile(_src, "graph_base_p0.py", "exec"), globals())

# --- P1 overlay (intent routing, turn policy, objection handoff) ---
_orig_prepare = _node_prepare  # type: ignore[name-defined]
_orig_parse = _node_parse  # type: ignore[name-defined]
_orig_actions = _node_actions  # type: ignore[name-defined]


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


def _node_actions(state):  # type: ignore[no-redef]
    """P2: prefer formal closer_registry; fallback to P0 closer_tools."""
    events: list[str] = list(state.get("events") or [])
    suffix_parts: list[str] = []
    action_results: list = list(state.get("action_results") or [])
    meta = state.get("meta") or {}
    lead = state.get("lead") or {}
    handoff_flag = bool(meta.get("handoff"))

    # Prefer registry (P2)
    try:
        from tools.closer_registry import execute_tool_calls_from_meta

        reg = execute_tool_calls_from_meta(
            workspace_id=state.get("workspace_id") or "",
            workspace_slug=state.get("workspace_slug") or "",
            lead=lead,
            meta=meta,
            playbook=None,
        )
        for note in reg.get("notes_for_reply") or []:
            if note and note not in suffix_parts:
                suffix_parts.append(str(note))
        for c in reg.get("calls") or []:
            action_results.append(c)
            if c.get("success"):
                events.append(f"tool:{c.get('name')}")
        if reg.get("handoff"):
            handoff_flag = True
            events.append("tool:request_handoff")
        events.append("closer_registry")
    except Exception:
        # Fallback P0 path
        try:
            out = _orig_actions(state)
            for k in ("action_results", "events", "reply_suffix"):
                if out.get(k) is not None:
                    if k == "events":
                        events.extend(out[k] or [])
                    elif k == "action_results":
                        action_results.extend(out[k] or [])
                    elif k == "reply_suffix" and out[k]:
                        suffix_parts.append(str(out[k]))
            if out.get("meta", {}).get("handoff") if isinstance(out.get("meta"), dict) else False:
                handoff_flag = True
            return {
                **out,
                "events": events,
                "action_results": action_results,
                "reply_suffix": "\n\n".join(suffix_parts) if suffix_parts else out.get("reply_suffix"),
            }
        except Exception:
            events.append("closer_tools_error")

    # Also run generic integrations actions if available (email/slack)
    try:
        from integrations.actions import run_agent_actions

        integ = run_agent_actions(
            workspace_id=state.get("workspace_id") or "",
            workspace_slug=state.get("workspace_slug") or "",
            lead=lead,
            meta=meta,
            agent=state.get("agent") or "sdr",
        )
        if isinstance(integ, dict):
            for r in integ.get("results") or []:
                action_results.append(r)
            if integ.get("reply_suffix"):
                suffix_parts.append(str(integ["reply_suffix"]))
            events.extend(integ.get("events") or [])
    except Exception:
        pass

    result = {
        "action_results": action_results,
        "events": events,
        "reply_suffix": "\n\n".join(suffix_parts) if suffix_parts else None,
    }
    if handoff_flag:
        m = dict(meta)
        m["handoff"] = True
        result["meta"] = m
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
