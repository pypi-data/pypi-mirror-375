# telemetry/logfire_sink.py
from __future__ import annotations
from typing import Any, Dict
from .base import TelemetrySink

class LogfireSink(TelemetrySink):
    """
    Thin adapter around logfire. Defaults to console OFF, but allows override via cfg.
    Default+pipe: {"console": False} | cfg
    """
    def __init__(self, **cfg: Any):
        self._lf = None
        self._emit = None
        try:
            import logfire  # type: ignore

            # Default console off; allow explicit override from caller.
            cfg = {"console": False} | dict(cfg or {})

            self._lf = logfire.configure(**cfg) if hasattr(logfire, "configure") else logfire

            # Optional Pydantic AI auto-instrumentation:
            if hasattr(self._lf, "instrument_pydantic_ai"):
                try:
                    self._lf.instrument_pydantic_ai()
                except Exception:
                    pass

            # Choose an emitter
            self._emit = (
                getattr(logfire, "event", None)
                or getattr(logfire, "info", None)
                or getattr(logfire, "log", None)
            )
        except Exception:
            self._lf, self._emit = None, None

    async def start(self, run_id: str, meta: Dict[str, Any]) -> None:
        if self._emit: self._emit("agent.start", run_id=run_id, **meta)

    async def step(self, run_id: str, name: str, payload: Dict[str, Any]) -> None:
        if self._emit: self._emit(f"agent.step.{name}", run_id=run_id, **payload)

    async def event(self, run_id: str, name: str, payload: Dict[str, Any]) -> None:
        if self._emit: self._emit(f"agent.event.{name}", run_id=run_id, **payload)

    async def error(self, run_id: str, payload: Dict[str, Any]) -> None:
        if self._emit: self._emit("agent.error", run_id=run_id, **payload)

    async def end(self, run_id: str, payload: Dict[str, Any]) -> None:
        if self._emit: self._emit("agent.end", run_id=run_id, **payload)
