from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable, Type

from botmark.runners import RunResponse, ProviderAdapter, OutputType
from .processors.base import BaseProcessor
from .processors.default import DefaultProcessor

class OpenAIAdapter(ProviderAdapter):
    def __init__(self, config: Dict[str, Any], *, get_processor_cls: Callable[[Optional[str]], Type[BaseProcessor]] | None = None):
        self.config = dict(config or {})
        self._get_processor_cls = get_processor_cls or (lambda _m: DefaultProcessor)

    @classmethod
    def is_valid_config(cls, config: Optional[Dict[str, Any]] = None) -> bool:
        return True

    async def run(
        self,
        input_text: str,
        *,
        message_history: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = "",
        tools: Optional[Any] = None,
        output_type: Optional[OutputType] = None,
        mcp_servers: Optional[List[Dict[str, Any]]] = None,
        links: Optional[List[Dict[str, Any]]] = None,
        images: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> RunResponse:

        # Users can force a processor by name if desired (advanced)
        forced = (self.config.get("processor") or "").strip().lower()
        model = self.config.get("model") or kwargs.get("model")

        ProcessorCls: Type[BaseProcessor]
        if forced:
            # allow "default" or "computer-use-preview"
            from .processors.default import DefaultProcessor
            from .processors.computer_use_preview import ComputerUsePreviewProcessor
            mapping = {
                "default": DefaultProcessor,
                "computer-use-preview": ComputerUsePreviewProcessor,
            }
            ProcessorCls = mapping.get(forced, DefaultProcessor)
        else:
            ProcessorCls = self._get_processor_cls(model)

        processor: BaseProcessor = ProcessorCls(self.config)

        return await processor.run(
            input_text=input_text,
            message_history=message_history,
            system_prompt=system_prompt,
            tools=tools,
            output_type=output_type,
            mcp_servers=mcp_servers,
            links=links,
            images=images,
            **kwargs,
        )
