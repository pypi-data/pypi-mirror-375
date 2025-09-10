from __future__ import annotations

from dataclasses import dataclass
import warnings, logging
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Type,
    Union,
    Mapping,
    TYPE_CHECKING,
    runtime_checkable,
)

logger = logging.getLogger(__name__)
Runner = Callable[..., Awaitable[Any]]

if TYPE_CHECKING:
    from pydantic import BaseModel

# Flexible output type alias
OutputType = Union[
    Mapping[str, Any],    # JSON-like dict
    "BaseModel",          # a Pydantic instance
    Type["BaseModel"],    # a Pydantic class
]

@dataclass
class RunResponse:
    output: Any
    all_messages: List[Dict[str, Any]]

OpenAIMessage = Dict[str, Any]

@runtime_checkable
class ProviderAdapter(Protocol):
    async def run(
        self,
        input_text: str,
        *,
        message_history: Optional[List[OpenAIMessage]] = None,
        system_prompt: Optional[str] = "",
        tools: Optional[Any] = None,
        output_type: Optional[OutputType] = None,
        mcp_servers: Optional[List[Dict[str, Any]]] = None,
        links: Optional[List[Dict[str, Any]]] = None,
        images: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> RunResponse: ...

    @classmethod
    def is_valid_config(cls, config: Optional[Dict[str, Any]] = None) -> bool: ...


ProviderFactory = Callable[[Optional[Dict[str, Any]]], ProviderAdapter]
_REGISTRY: Dict[str, ProviderFactory] = {}


def register_provider(name: str, factory: ProviderFactory) -> None:
    _REGISTRY[name.lower()] = factory


# ---- NEW: runner wrapper with metadata --------------------------------------

@dataclass
class _RunnerWrapper:
    """
    Callable Runner with framework/config metadata.
    Keeps awaitable semantics via __call__ and exposes get_info().
    """
    provider: str
    config: Dict[str, Any]
    adapter: ProviderAdapter

    # handy aliases if other code expects these names
    @property
    def framework_name(self) -> str:
        return self.provider

    @property
    def framework_config(self) -> Dict[str, Any]:
        return self.config

    def get_info(self) -> Dict[str, Any]:
        cls = self.adapter.__class__
        return {
            "framework": self.provider,
            "config": self.config,
            "adapter_class": f"{cls.__module__}.{cls.__name__}",
        }

    async def __call__(self, input_text: str, **kwargs: Any) -> Any:
        # Mirror the prior forwarding logic, while preserving compatibility
        system_prompt = kwargs.pop("system_prompt", "")
        message_history = kwargs.pop("message_history", None)
        tools = kwargs.pop("tools", None)
        return await self.adapter.run(
            input_text,
            message_history=message_history,
            system_prompt=system_prompt,
            tools=tools,
            **kwargs,
        )


def create_ai_runner(provider: str = "pydanticai", config: Optional[Dict[str, Any]] = None) -> Runner:
    name = provider.lower()
    if name not in _REGISTRY:
        async def unsupported(*_: Any, **__: Any) -> Any:
            raise NotImplementedError(f"Unsupported provider '{provider}'")
        # Provide basic metadata even for unsupported provider
        setattr(unsupported, "framework_name", provider)
        setattr(unsupported, "framework_config", config or {})
        setattr(unsupported, "get_info", lambda: {
            "framework": provider,
            "config": config or {},
            "error": "Unsupported provider",
        })
        return unsupported

    adapter = _REGISTRY[name](config or {})
    # Return a callable object carrying metadata
    return _RunnerWrapper(provider=name, config=config or {}, adapter=adapter)

def is_valid_config(provider: str, config: Optional[Dict[str, Any]] = None) -> bool:
    name = provider.lower()
    if name not in _REGISTRY:
        logger.warning( f"Invalid provider: {provider}" )
        return False

    factory = _REGISTRY[name]

    # Get the adapter class, not instance
    adapter_cls = factory.__annotations__.get("return")  # type hint if available
    adapter = factory(config or {})

    # Try to call the classmethod directly if present
    cls_method = getattr(adapter.__class__, "is_valid_config", None)
    if not callable(cls_method):
        raise NotImplementedError(
            f"Provider '{provider}' does not implement classmethod is_valid_config(config)."
        )
    return bool(cls_method(config or {}))

def safe_register(name: str, import_path: str, factory_attr: str = "factory") -> None:
    try:
        module = __import__(import_path, fromlist=[factory_attr])
        factory = getattr(module, factory_attr)
        register_provider(name, factory)
    except Exception as e:
        warnings.warn(
            f"Provider '{name}' could not be registered ({import_path}): {e}",
            category=ImportWarning,
            stacklevel=2,
        )


# --- Built-in registrations ---

try:
    from .providers.pydanticai_adapter import factory as _pydanticai_factory
    register_provider("pydantic-ai", _pydanticai_factory)
except Exception as e:
    warnings.warn(
        f"Provider 'pydantic-ai' could not be registered: {e}",
        category=ImportWarning,
        stacklevel=2,
    )

try:
    from .providers.openai_agents_adapter import factory as _oa_agents_factory
    register_provider("openai-agents", _oa_agents_factory)
except Exception as e:
    warnings.warn(
        f"Provider 'openai-agents' could not be registered: {e}",
        category=ImportWarning,
        stacklevel=2,
    )

try:
    from .providers.langgraph_adapter import factory as _lg_factory
    register_provider("langgraph", _lg_factory)
except Exception as e:
    warnings.warn(
        f"Provider 'langgraph' could not be registered: {e}",
        category=ImportWarning,
        stacklevel=2,
    )

# wherever you register providers
import warnings
from .providers.openai_adapter import factory as _oa_factory

try:
    register_provider("openai", _oa_factory)
except Exception as e:
    warnings.warn(
        f"Provider 'openai' could not be registered: {e}",
        category=ImportWarning,
        stacklevel=2,
    )
