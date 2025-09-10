from __future__ import annotations
from typing import Optional, Dict, Any, Callable, Type

from .adapter import OpenAIAdapter
from .processors.base import BaseProcessor
from .processors.default import DefaultProcessor
from .processors.computer_use_preview import ComputerUsePreviewProcessor

_MODEL_PROCESSORS: dict[str, Type[BaseProcessor]] = {
    "computer-use-preview": ComputerUsePreviewProcessor,
}
_PREDICATE_PROCESSORS: list[tuple[Callable[[str], bool], Type[BaseProcessor]]] = []

def register_processor_for_model(model: str, processor_cls: Type[BaseProcessor]) -> None:
    _MODEL_PROCESSORS[model] = processor_cls

def register_processor_predicate(predicate: Callable[[str], bool], processor_cls: Type[BaseProcessor]) -> None:
    _PREDICATE_PROCESSORS.append((predicate, processor_cls))

def get_processor_cls(model: Optional[str]) -> Type[BaseProcessor]:
    if not model:
        return DefaultProcessor
    if model in _MODEL_PROCESSORS:
        return _MODEL_PROCESSORS[model]
    for pred, cls in _PREDICATE_PROCESSORS:
        try:
            if pred(model):
                return cls
        except Exception:
            continue
    return DefaultProcessor

def factory(config: Optional[Dict[str, Any]] = None) -> OpenAIAdapter:
    return OpenAIAdapter(config or {}, get_processor_cls=get_processor_cls)

__all__ = [
    "factory",
    "register_processor_for_model",
    "register_processor_predicate",
    "OpenAIAdapter",
]
