# telemetry/base.py
from __future__ import annotations
import asyncio
import time
from typing import Any, Dict, List, Protocol, Optional

class TelemetrySink(Protocol):
    async def start(self, run_id: str, meta: Dict[str, Any]) -> None: ...
    async def step(self, run_id: str, name: str, payload: Dict[str, Any]) -> None: ...
    async def event(self, run_id: str, name: str, payload: Dict[str, Any]) -> None: ...
    async def error(self, run_id: str, payload: Dict[str, Any]) -> None: ...
    async def end(self, run_id: str, payload: Dict[str, Any]) -> None: ...

class NoOpTelemetrySink:
    async def start(self, run_id: str, meta: Dict[str, Any]) -> None: return None
    async def step(self, run_id: str, name: str, payload: Dict[str, Any]) -> None: return None
    async def event(self, run_id: str, name: str, payload: Dict[str, Any]) -> None: return None
    async def error(self, run_id: str, payload: Dict[str, Any]) -> None: return None
    async def end(self, run_id: str, payload: Dict[str, Any]) -> None: return None

class CompositeTelemetrySink:
    """Fan-out to multiple sinks (e.g., Logfire + Langfuse)."""
    def __init__(self, sinks: List[TelemetrySink]):
        self._sinks = list(sinks or [])

    async def start(self, run_id: str, meta: Dict[str, Any]) -> None:
        await asyncio.gather(*(s.start(run_id, meta) for s in self._sinks))

    async def step(self, run_id: str, name: str, payload: Dict[str, Any]) -> None:
        await asyncio.gather(*(s.step(run_id, name, payload) for s in self._sinks))

    async def event(self, run_id: str, name: str, payload: Dict[str, Any]) -> None:
        await asyncio.gather(*(s.event(run_id, name, payload) for s in self._sinks))

    async def error(self, run_id: str, payload: Dict[str, Any]) -> None:
        await asyncio.gather(*(s.error(run_id, payload) for s in self._sinks))

    async def end(self, run_id: str, payload: Dict[str, Any]) -> None:
        await asyncio.gather(*(s.end(run_id, payload) for s in self._sinks))

class StepTimer:
    """Use with 'async with' to time and emit a step automatically."""
    def __init__(self, sink: TelemetrySink, run_id: str, name: str, extra: Optional[Dict[str, Any]] = None):
        self.sink, self.run_id, self.name = sink, run_id, name
        self.extra = extra or {}
        self.t0 = 0.0

    async def __aenter__(self):
        self.t0 = time.perf_counter()
        await self.sink.step(self.run_id, f"{self.name}.start", dict(self.extra))
        return self

    async def __aexit__(self, exc_type, exc, tb):
        dur = time.perf_counter() - self.t0
        payload = dict(self.extra)
        payload["duration_s"] = round(dur, 6)
        if exc:
            payload["exception_type"] = getattr(exc_type, "__name__", str(exc_type))
            payload["exception"] = str(exc)
            await self.sink.error(self.run_id, payload)
        else:
            await self.sink.step(self.run_id, f"{self.name}.end", payload)
        return False  # don't suppress exceptions
