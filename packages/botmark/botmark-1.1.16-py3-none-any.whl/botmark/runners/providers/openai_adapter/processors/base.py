from __future__ import annotations
from typing import Any, Dict, List, Optional
from botmark.runners import RunResponse, OutputType

class BaseProcessor:
    """
    Interface for model processors.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = dict(config or {})

    async def run(
        self,
        *,
        input_text: str,
        message_history: Optional[List[Dict[str, Any]]],
        system_prompt: Optional[str],
        tools: Optional[Any],
        output_type: Optional[OutputType],
        mcp_servers: Optional[List[Dict[str, Any]]],
        links: Optional[List[Dict[str, Any]]],
        images: Optional[List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> RunResponse:
        raise NotImplementedError
