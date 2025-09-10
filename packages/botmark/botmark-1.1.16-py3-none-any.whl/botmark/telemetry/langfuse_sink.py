# telemetry/langfuse_sink.py
from __future__ import annotations
from typing import Any, Dict
from .base import TelemetrySink

class LangfuseSink(TelemetrySink):
    """
    Minimal Langfuse adapter. Uses a single trace per agent run and emits
    steps as events/spans as available. Gracefully no-ops if SDK missing.
    """
    def __init__(self, **cfg: Any):
        self._lf = None
        self._trace = None
        self._cfg = cfg
        try:
            from langfuse import Langfuse  # type: ignore
            self._lf = Langfuse(**cfg)
        except Exception:
            self._lf = None

    async def start(self, run_id: str, meta: Dict[str, Any]) -> None:
        if not self._lf: return
        try:
            self._trace = self._lf.trace(id=run_id, name="botmark-agent-run", input=meta)  # type: ignore[attr-defined]
        except Exception:
            try:
                self._trace = self._lf.create_trace(id=run_id, name="botmark-agent-run", input=meta)  # type: ignore[attr-defined]
            except Exception:
                self._trace = None

    async def step(self, run_id: str, name: str, payload: Dict[str, Any]) -> None:
        if not self._lf: return
        try:
            if self._trace and hasattr(self._trace, "event"):
                self._trace.event(name=name, data=payload)  # type: ignore[attr-defined]
            else:
                if hasattr(self._lf, "event"):
                    self._lf.event(name=name, data=payload, trace_id=run_id)  # type: ignore[attr-defined]
        except Exception:
            pass

    async def event(self, run_id: str, name: str, payload: Dict[str, Any]) -> None:
        await self.step(run_id, name, payload)

    async def error(self, run_id: str, payload: Dict[str, Any]) -> None:
        await self.step(run_id, "error", payload)

    async def end(self, run_id: str, payload: Dict[str, Any]) -> None:
        if not self._lf: return
        try:
            if self._trace and hasattr(self._trace, "end"):
                self._trace.end(output=payload)  # type: ignore[attr-defined]
        except Exception:
            pass
