# telemetry/factory.py
from __future__ import annotations
from typing import Any, Dict, Optional, List, Union
from .base import TelemetrySink, NoOpTelemetrySink, CompositeTelemetrySink
from .logfire_sink import LogfireSink
from .langfuse_sink import LangfuseSink

def create_telemetry(config: Optional[Union[str, Dict[str, Any]]] = None) -> TelemetrySink:
    """
    Accepts:
      - None / "noop" → NoOp
      - "logfire" or {"logfire": {...}}
      - "langfuse" or {"langfuse": {...}}
      - {"multi": {"logfire": {...}, "langfuse": {...}}}
    """
    if config is None or config == "noop":
        return NoOpTelemetrySink()

    if isinstance(config, str):
        key = config.strip().lower()
        if key == "logfire":
            return LogfireSink()
        if key == "langfuse":
            return LangfuseSink()
        return NoOpTelemetrySink()

    if not isinstance(config, dict):
        return NoOpTelemetrySink()

    if "multi" in config and isinstance(config["multi"], dict):
        sinks: List[TelemetrySink] = []
        mf = config["multi"]
        if "logfire" in mf: sinks.append(LogfireSink(**(mf["logfire"] or {})))
        if "langfuse" in mf: sinks.append(LangfuseSink(**(mf["langfuse"] or {})))
        return CompositeTelemetrySink(sinks)

    if "logfire" in config:
        return LogfireSink(**(config["logfire"] or {}))

    if "langfuse" in config:
        return LangfuseSink(**(config["langfuse"] or {}))

    return NoOpTelemetrySink()
