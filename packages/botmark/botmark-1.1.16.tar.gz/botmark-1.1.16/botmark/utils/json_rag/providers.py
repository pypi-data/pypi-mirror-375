from __future__ import annotations
import os, warnings
from typing import Protocol, Sequence, List, Optional

class EmbeddingProvider(Protocol):
    def embed(self, texts: Sequence[str], *, normalize: bool = True) -> List[List[float]]:
        ...
    @property
    def tag(self) -> str: ...

def _l2_normalize(vec: List[float]) -> List[float]:
    import math
    n = math.sqrt(sum(v*v for v in vec)) or 1.0
    return [v/n for v in vec]

def _fallback_embeddings(texts: Sequence[str]) -> List[List[float]]:
    """
    Deterministic fallback: represent each string as [len(text)].
    Not useful semantically, but avoids crashing.
    """
    warnings.warn("[json_rag] Using fallback embeddings (provider not available).", RuntimeWarning)
    return [[float(len(t))] for t in texts]

class SentenceTransformersProvider:
    """
    Requires: pip install sentence-transformers
    Falls back gracefully if import fails.
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self._model_name = model_name
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model_name)
            self._ok = True
        except Exception as e:
            warnings.warn(f"[json_rag] SentenceTransformers not available ({e}); using fallback.", RuntimeWarning)
            self._model = None
            self._ok = False

    @property
    def tag(self) -> str:
        return f"st/{self._model_name}"

    def embed(self, texts: Sequence[str], *, normalize: bool = True) -> List[List[float]]:
        if not self._ok or self._model is None:
            return _fallback_embeddings(texts)
        vecs = self._model.encode(list(texts), convert_to_numpy=True, normalize_embeddings=False)
        out: List[List[float]] = []
        for i in range(len(texts)):
            row = vecs[i].tolist()
            if normalize:
                row = _l2_normalize(row)
            out.append(row)
        return out

class OpenAIEmbeddingProvider:
    """
    Requires: pip install openai
    Env: OPENAI_API_KEY
    Falls back gracefully if import or API call fails.
    """
    def __init__(self, model: str = "text-embedding-3-small", api_key: Optional[str] = None):
        self._model = model
        try:
            from openai import OpenAI
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY missing.")
            self._client = OpenAI(api_key=api_key)
            self._ok = True
        except Exception as e:
            warnings.warn(f"[json_rag] OpenAI not available ({e}); using fallback.", RuntimeWarning)
            self._client = None
            self._ok = False

    @property
    def tag(self) -> str:
        return f"openai/{self._model}"

    def embed(self, texts: Sequence[str], *, normalize: bool = True) -> List[List[float]]:
        if not self._ok or self._client is None:
            return _fallback_embeddings(texts)
        try:
            resp = self._client.embeddings.create(model=self._model, input=list(texts))
            out: List[List[float]] = []
            for d in resp.data:
                row = list(d.embedding)
                if normalize:
                    row = _l2_normalize(row)
                out.append(row)
            return out
        except Exception as e:
            warnings.warn(f"[json_rag] OpenAI API call failed ({e}); using fallback.", RuntimeWarning)
            return _fallback_embeddings(texts)

class AzureOpenAIEmbeddingProvider:
    """
    Requires: pip install openai  (v1+)
    Env (recommended):
      AZURE_OPENAI_API_KEY
      AZURE_OPENAI_ENDPOINT      e.g. "https://<your-resource>.openai.azure.com/"
      AZURE_OPENAI_API_VERSION   e.g. "2024-08-01-preview"
      AZURE_OPENAI_EMBEDDING_DEPLOYMENT  e.g. "text-embedding-3-small"

    Note: In Azure, the `model` you pass is the *deployment name*, not the raw model id.
    """
    def __init__(
        self,
        *,
        deployment: Optional[str] = None,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        self._deployment = deployment or os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") or ""
        try:
            from openai import AzureOpenAI
            api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
            endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
            api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION") or "2024-08-01-preview"

            if not api_key:
                raise ValueError("AZURE_OPENAI_API_KEY missing.")
            if not endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT missing.")
            if not self._deployment:
                raise ValueError("Azure embedding deployment name missing (set AZURE_OPENAI_EMBEDDING_DEPLOYMENT).")

            self._client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint,
            )
            self._ok = True
        except Exception as e:
            warnings.warn(f"[json_rag] AzureOpenAI not available ({e}); using fallback.", RuntimeWarning)
            self._client = None
            self._ok = False

    @property
    def tag(self) -> str:
        # e.g. "azure-openai/text-embedding-3-small"
        return f"azure-openai/{self._deployment or 'unknown-deployment'}"

    def embed(self, texts: Sequence[str], *, normalize: bool = True) -> List[List[float]]:
        if not self._ok or self._client is None:
            return _fallback_embeddings(texts)
        try:
            # In Azure, pass the deployment name as `model`
            resp = self._client.embeddings.create(model=self._deployment, input=list(texts))
            out: List[List[float]] = []
            for d in resp.data:
                row = list(d.embedding)
                if normalize:
                    row = _l2_normalize(row)
                out.append(row)
            return out
        except Exception as e:
            warnings.warn(f"[json_rag] Azure OpenAI embeddings failed ({e}); using fallback.", RuntimeWarning)
            return _fallback_embeddings(texts)