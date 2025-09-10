"""
json_rag package
- apply_json_rag(blocks: dict, rag_query: str) -> dict
- Indexing & ranking helpers via submodules
"""

import os
from typing import List, Dict, Any
from .providers import EmbeddingProvider, SentenceTransformersProvider, OpenAIEmbeddingProvider, AzureOpenAIEmbeddingProvider
from .db import open_db
from .utils import default_stringify, _make_stringify_from_attrs
from .rank import (
    index_items,
    rank_items_with_db,
    rank_items_in_memory,
    ensure_embeddings_for_items,
)

import logging
logger = logging.getLogger(__name__)

# ===== HARD-CODED TOGGLES (no env, no attribute) =====
# Use the DB (stored embeddings) or embed on-the-fly:
USE_DB = True
# When USE_DB is True, automatically backfill missing embeddings for the current items:
AUTO_BACKFILL = True

# simple caches so we don't recreate clients/DB per block
_embedder_cache = {}
_conn_cache = {}

def _get_embedder(provider_choice: str, st_model: str, openai_model: str):
    key = (provider_choice, st_model, openai_model)
    if key in _embedder_cache:
        return _embedder_cache[key]
    if provider_choice == "openai":
        emb = OpenAIEmbeddingProvider(model=openai_model)
    elif provider_choice.startswith("azure"):
        emb = AzureOpenAIEmbeddingProvider()
    else:
        emb = SentenceTransformersProvider(st_model)
    _embedder_cache[key] = emb
    return emb

def _get_conn(db_path: str):
    if db_path in _conn_cache:
        return _conn_cache[db_path]
    conn = open_db(db_path)
    _conn_cache[db_path] = conn
    return conn

def _assign_block_content(block: dict, data):
    """Support both dict-style and optional block.set('content', ...) API."""
    setter = getattr(block, "set", None)
    if callable(setter):
        try:
            setter("content", data)
            return
        except Exception:
            pass
    block["content"] = data

def apply_json_rag(blocks: dict, query: str, history ) -> dict:
    """
    Sort JSON blocks by relevance to `rag_query`.
    DB usage is controlled solely by the hard-coded USE_DB flag in this module.
    """

    # These still come from env or block attributes; only the DB toggle is code-level.
    provider_choice_default = os.getenv("PROVIDER", "st").lower()
    st_model_default = os.getenv("ST_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    openai_model_default = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
    db_path_default = os.getenv("DB_PATH", "data/embeddings.db")
    length_threshold_default = int(os.getenv("LENGTH_THRESHOLD", "60"))
    context_size = int(os.getenv("CONTEXT_SIZE", "2000"))
    rag_query = rag_reduce_weighted_slices( history, include_role_labels=False, max_length=context_size) + query

    for key, block in blocks.items():
        try:
            logger.debug(f"[json_rag] Processing block '{key}'…")

            if block.get("language") != "json":
                logger.debug(f"[json_rag] Block '{key}' skipped (language={block.get('language')}).")
                continue

            classes = block.get("classes", []) or []
            attrs = block.get("attributes", {}) or {}
            if not (("rag" in classes) or ("rag_key" in attrs)):
                logger.debug(f"[json_rag] Block '{key}' skipped (no rag trigger).")
                continue

            data = block.get("content")
            if not isinstance(data, list):
                logger.warning(f"[json_rag] Block '{key}' skipped (content not a list).")
                continue

            provider_choice = str(attrs.get("provider", provider_choice_default)).lower()
            st_model = str(attrs.get("st_model", st_model_default))
            openai_model = str(attrs.get("openai_model", openai_model_default))
            db_path = str(attrs.get("db_path", db_path_default))
            length_threshold = int(attrs.get("length_threshold", length_threshold_default))
            on_missing = str(attrs.get("on_missing", "zero")).lower()  # only used in DB mode
            top_k = attrs.get("top_k")
            try:
                top_k = int(top_k) if top_k is not None else None
            except Exception:
                top_k = None

            logger.debug(
                f"[json_rag] Block '{key}' config → provider={provider_choice}, "
                f"st_model={st_model}, openai_model={openai_model}, db_path={db_path}, "
                f"USE_DB={USE_DB}, len(data)={len(data)}, length_threshold={length_threshold}, "
                f"top_k={top_k}, on_missing={on_missing}"
            )

            # stringify (respects rag_key if provided)
            sf = _make_stringify_from_attrs(attrs, default_stringify)
            embedder = _get_embedder(provider_choice, st_model, openai_model)

            if USE_DB:
                logger.debug(f"[json_rag] Using DB mode for block '{key}' with query: {rag_query!r}")
                conn = _get_conn(db_path)

                if AUTO_BACKFILL:
                    inserted = ensure_embeddings_for_items(
                        conn=conn,
                        embedder=embedder,
                        items=data,
                        stringify=sf,
                        length_threshold=length_threshold,
                    )
                    if inserted:
                        logger.debug(f"[json_rag] Block '{key}': backfilled {inserted} embeddings.")

                ranked_with_scores = rank_items_with_db(
                    conn=conn,
                    embedder=embedder,
                    items=data,
                    query=rag_query,
                    stringify=sf,
                    length_threshold=length_threshold,
                    top_k=top_k,
                    return_scores=True,
                    on_missing=on_missing,
                )
            else:
                logger.debug(f"[json_rag] Using IN-MEMORY mode for block '{key}' with query: {rag_query!r}")
                ranked_with_scores = rank_items_in_memory(
                    embedder=embedder,
                    items=data,
                    query=rag_query,
                    stringify=sf,
                    length_threshold=length_threshold,
                    top_k=top_k,
                    return_scores=True,
                )

            logger.debug(f"[json_rag] Ranked results for block '{key}':")
            for item, score in ranked_with_scores:
                label = item.get("name") or item.get("title") or str(item)[:30]
                logger.debug(f"   {score:6.3f}  {label}")

            ranked_items = [it for it, _ in ranked_with_scores]
            _assign_block_content(block, ranked_items)

        except Exception as e:
            logger.debug(f"[json_rag] Block '{key}' error: {e}")

    return blocks


def _content_to_text(msg: Dict[str, Any]) -> str:
    """
    Normalize OpenAI message content:
      - string content
      - list of parts: {"type":"text"|"image_url"|...}
      - assistant tool_calls are collapsed briefly
    """
    content = msg.get("content", "")
    out = []

    # Assistant tool_calls (brief summary)
    tcs = msg.get("tool_calls") or []
    if tcs and msg.get("role") == "assistant":
        brief = []
        for tc in tcs:
            if tc.get("type") == "function":
                fn = tc.get("function", {})
                name = fn.get("name", "function")
                args = str(fn.get("arguments", ""))
                if len(args) > 120:
                    args = args[:117] + "..."
                brief.append(f"{name}({args})")
            else:
                brief.append("tool_call")
        out.append(f"[tool_calls: {', '.join(brief)}]")

    if isinstance(content, str):
        out.append(content)
    elif isinstance(content, list):
        for part in content:
            ptype = part.get("type")
            if ptype == "text":
                out.append(part.get("text", ""))
            elif ptype == "image_url":
                out.append("[image]")
            else:
                out.append(f"[{ptype or 'part'}]")
    else:
        out.append(str(content))

    text = "\n".join(out)
    text = text.replace("\r", "")
    while "  " in text:
        text = text.replace("  ", " ")
    text = "\n".join(line.strip() for line in text.split("\n")).strip()
    return text


def rag_reduce_weighted_slices(
    messages: List[Dict[str, Any]],
    max_length: int = 4000,
    recent_bias: float = 1.6,
    min_per_msg: int = 24,
    include_roles=("user", "assistant", "tool", "function"),
    include_role_labels: bool = True,
    include_system: bool = False,   # <-- flag renamed, default False
) -> str:
    """
    Reduce an OpenAI-style message list to a single <= max_length string.

    Strategy:
      - By default excludes `system` messages (`include_system=False`).
      - Slice each message text with variable size; newer messages get bigger pieces.
      - Geometric weighting via `recent_bias`.
      - Hard cap by characters.

    Args:
        messages: OpenAI message history (list of dicts).
        max_length: Max characters allowed.
        recent_bias: >1 => newer messages get larger allocations.
        min_per_msg: Minimum chars per message if possible.
        include_roles: Roles to consider.
        include_role_labels: Whether to prefix with "User:", "Assistant:", etc.
        include_system: If True, includes system messages.
    """
    import json
    result = json.dumps ( messages )

    if max_length is not None and len(result) > max_length:
        return result[:max_length]
    return result
