"""
ForceIA - Observabilidade via Langfuse.

Trace completo de cada turno:
  forceia.turn
    ├─ prepare
    ├─ generation (LLM)
    ├─ parse (META / BANT / stage)
    ├─ route (transicao)
    └─ persist (DB / WhatsApp / CRM)

Env:
  LANGFUSE_PUBLIC_KEY
  LANGFUSE_SECRET_KEY
  LANGFUSE_HOST          # default https://cloud.langfuse.com
  LANGFUSE_ENABLED=1     # 0 desliga mesmo com chaves

Sem chaves: no-op (nao quebra o runtime).
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator

_client = None
_init_attempted = False


def enabled() -> bool:
    flag = os.getenv("LANGFUSE_ENABLED", "1").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    return bool(
        os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
    )


def get_client():
    global _client, _init_attempted
    if _client is not None:
        return _client
    if _init_attempted:
        return None
    _init_attempted = True
    if not enabled():
        return None
    try:
        from langfuse import Langfuse

        _client = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").rstrip("/"),
        )
        return _client
    except Exception:
        return None


def flush() -> None:
    client = get_client()
    if client is None:
        return
    try:
        client.flush()
    except Exception:
        pass


@dataclass
class TurnTrace:
    name: str = "forceia.turn"
    trace_id: str | None = None
    _trace: Any = None
    _spans: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def span(self, name: str, **metadata: Any) -> "_Span":
        return _Span(self, name, metadata)

    def event(self, name: str, **metadata: Any) -> None:
        if self._trace is None:
            return
        try:
            if hasattr(self._trace, "event"):
                self._trace.event(name=name, metadata=metadata or None)
            else:
                client = get_client()
                if client and hasattr(client, "event"):
                    client.event(trace_id=self.trace_id, name=name, metadata=metadata or None)
        except Exception:
            pass

    def generation(
        self,
        *,
        name: str = "llm",
        model: str | None = None,
        input: Any = None,
        output: Any = None,
        metadata: dict | None = None,
        usage: dict | None = None,
        level: str = "DEFAULT",
    ) -> None:
        if self._trace is None:
            return
        try:
            kwargs: dict[str, Any] = {
                "name": name,
                "model": model,
                "input": input,
                "output": output,
                "metadata": metadata or {},
            }
            if usage:
                kwargs["usage"] = usage
            if hasattr(self._trace, "generation"):
                self._trace.generation(**kwargs)
            else:
                client = get_client()
                if client and hasattr(client, "generation"):
                    client.generation(trace_id=self.trace_id, **kwargs)
        except Exception:
            pass

    def update(self, **kwargs: Any) -> None:
        if self._trace is None:
            return
        try:
            if hasattr(self._trace, "update"):
                self._trace.update(**kwargs)
        except Exception:
            pass

    def end(self, *, output: Any = None, metadata: dict | None = None) -> None:
        if self._trace is None:
            return
        try:
            payload: dict[str, Any] = {}
            if output is not None:
                payload["output"] = output
            if metadata:
                payload["metadata"] = {**(self.metadata or {}), **metadata}
            if payload and hasattr(self._trace, "update"):
                self._trace.update(**payload)
            flush()
        except Exception:
            pass


@dataclass
class _Span:
    parent: TurnTrace
    name: str
    metadata: dict
    _span: Any = None
    _t0: float = 0.0

    def __enter__(self) -> "_Span":
        self._t0 = time.time()
        if self.parent._trace is None:
            return self
        try:
            if hasattr(self.parent._trace, "span"):
                self._span = self.parent._trace.span(
                    name=self.name, metadata=self.metadata or None
                )
            elif hasattr(self.parent._trace, "start_span"):
                self._span = self.parent._trace.start_span(
                    name=self.name, metadata=self.metadata or None
                )
        except Exception:
            self._span = None
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        duration_ms = int((time.time() - self._t0) * 1000)
        if self._span is None:
            return
        try:
            meta = dict(self.metadata or {})
            meta["duration_ms"] = duration_ms
            if exc is not None:
                if hasattr(self._span, "end"):
                    self._span.end(level="ERROR", status_message=str(exc)[:500], metadata=meta)
                elif hasattr(self._span, "update"):
                    self._span.update(level="ERROR", status_message=str(exc)[:500], metadata=meta)
            else:
                if hasattr(self._span, "end"):
                    self._span.end(metadata=meta)
                elif hasattr(self._span, "update"):
                    self._span.update(metadata=meta)
        except Exception:
            pass

    def update(self, **kwargs: Any) -> None:
        if self._span is None:
            return
        try:
            if hasattr(self._span, "update"):
                self._span.update(**kwargs)
        except Exception:
            pass


def start_turn_trace(
    *,
    workspace_id: str,
    workspace_slug: str,
    phone: str,
    stage: str | None = None,
    agent: str | None = None,
    user_message: str | None = None,
    lead_id: str | None = None,
    session_id: str | None = None,
    tags: list[str] | None = None,
) -> TurnTrace:
    client = get_client()
    meta = {
        "workspace_id": workspace_id,
        "workspace_slug": workspace_slug,
        "phone": phone,
        "stage": stage,
        "agent": agent,
        "lead_id": lead_id,
        "product": "forceia",
    }
    session = session_id or f"{workspace_id}:{phone}"
    tag_list = list(tags or [])
    if workspace_slug:
        tag_list.append(f"ws:{workspace_slug}")
    if agent:
        tag_list.append(f"agent:{agent}")
    if stage:
        tag_list.append(f"stage:{stage}")

    if client is None:
        return TurnTrace(metadata=meta)

    try:
        if hasattr(client, "trace"):
            tr = client.trace(
                name="forceia.turn",
                session_id=session,
                user_id=phone,
                input={"message": (user_message or "")[:2000]},
                metadata=meta,
                tags=tag_list,
            )
            tid = getattr(tr, "id", None) or getattr(tr, "trace_id", None)
            return TurnTrace(trace_id=tid, _trace=tr, metadata=meta)
        if hasattr(client, "start_span"):
            tr = client.start_span(
                name="forceia.turn",
                metadata=meta,
                input={"message": (user_message or "")[:2000]},
            )
            tid = getattr(tr, "trace_id", None) or getattr(tr, "id", None)
            return TurnTrace(trace_id=tid, _trace=tr, metadata=meta)
    except Exception:
        pass
    return TurnTrace(metadata=meta)


@contextmanager
def observe_turn(**kwargs: Any) -> Iterator[TurnTrace]:
    tr = start_turn_trace(**kwargs)
    try:
        yield tr
    finally:
        tr.end()
