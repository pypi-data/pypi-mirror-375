from __future__ import annotations
import os
from typing import Any, Dict, Optional
from contextlib import AsyncExitStack

try:
    from openai import AsyncOpenAI, AsyncAzureOpenAI
except Exception as e:
    raise ImportError("The openai package is required. Install with: pip install -U openai") from e

def resolve_client(cfg: Dict[str, Any]) -> Optional[object]:
    required_openai = ["api_key"]
    required_azure = ["api_key", "api_version", "azure_endpoint", "azure_deployment"]

    def is_complete(d: Dict[str, Any], required: list[str]) -> bool:
        return all(d.get(k) for k in required)

    if is_complete(cfg, required_openai):
        return AsyncOpenAI(api_key=cfg["api_key"], base_url=cfg.get("base_url", "https://api.openai.com/v1"))
    if is_complete(cfg, required_azure):
        return AsyncAzureOpenAI(
            api_key=cfg["api_key"],
            api_version=cfg["api_version"],
            azure_endpoint=cfg["azure_endpoint"],
            azure_deployment=cfg["azure_deployment"],
        )

    env_openai = {"api_key": os.getenv("OPENAI_API_KEY"), "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")}
    if is_complete(env_openai, required_openai):
        return AsyncOpenAI(**env_openai)

    env_azure = {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
        "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "azure_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    }
    if is_complete(env_azure, required_azure):
        return AsyncAzureOpenAI(**env_azure)

    return None


class ClientContext:
    """
    Async context wrapper to ensure the SDK’s httpx client is closed while the loop is alive.
    """
    def __init__(self, client):
        self.client = client

    async def __aenter__(self):
        return self.client

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await self.client.close()
        except Exception:
            pass
