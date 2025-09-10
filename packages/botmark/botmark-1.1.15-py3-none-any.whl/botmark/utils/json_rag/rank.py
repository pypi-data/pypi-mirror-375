from __future__ import annotations
from typing import Sequence, List, Tuple, Optional, Any
from .providers import EmbeddingProvider
from .utils import default_stringify, make_keys_for_items, dot
from .db import ensure_model, upsert_embeddings, load_vectors_for_keys
import sqlite3

import logging
logger = logging.getLogger(__name__)

def index_items(
    *,
    conn: sqlite3.Connection,
    embedder: EmbeddingProvider,
    items: Sequence[Any],
    stringify=default_stringify,
    length_threshold: int = 180,
    metas: Optional[Sequence[dict]] = None,
) -> List[str]:
    model_id, _info = ensure_model(conn, embedder)
    keys, texts = make_keys_for_items(items, stringify, length_threshold)
    embs = embedder.embed(texts, normalize=True)
    upsert_embeddings(conn, model_id, list(zip(keys, embs)), metas=list(metas) if metas else None)
    return keys

def rank_items_with_db(
    *,
    conn: sqlite3.Connection,
    embedder: EmbeddingProvider,
    items: Sequence[Any],
    query: str,
    stringify=default_stringify,
    length_threshold: int = 180,
    top_k: Optional[int] = None,
    return_scores: bool = False,
    on_missing: str = "zero",  # "error" | "skip" | "zero"
):
    model_id, _info = ensure_model(conn, embedder)
    keys, _texts = make_keys_for_items(items, stringify, length_threshold)
    logger.debug(f"[json_rag][DB] model_id={model_id}, items={len(items)}, length_threshold={length_threshold}")
    if len(keys) <= 5:
        logger.debug("[json_rag][DB] keys:" + str(keys))

    doc_mat, found, dim_d = load_vectors_for_keys(conn, model_id, keys)
    found_cnt = sum(1 for x in found if x)
    logger.debug(f"[json_rag][DB] embeddings found: {found_cnt}/{len(keys)} (provider={embedder.tag})")

    if not doc_mat:
        logger.debug("[json_rag][DB] no vectors loaded from DB")
        return [] if return_scores else []

    q_vec = embedder.embed([query], normalize=True)[0]
    if len(q_vec) != dim_d:
        raise ValueError(f"Dimension mismatch: query dim={len(q_vec)} vs doc dim={dim_d}. "
                         f"Did you index with a different provider/model?")

    scores: List[float] = []
    for i, (vec, ok) in enumerate(zip(doc_mat, found)):
        if not ok:
            if on_missing == "skip":
                scores.append(float("-inf"))
            elif on_missing == "error":
                raise ValueError(f"Missing embedding for key[{i}]={keys[i]!r}")
            else:
                scores.append(0.0)
        else:
            scores.append(dot(vec, q_vec))

    order = sorted(range(len(items)), key=lambda i: scores[i], reverse=True)
    if top_k is not None:
        order = order[:top_k]

    if return_scores:
        return [(items[i], scores[i]) for i in order if scores[i] != float("-inf")]
    return [items[i] for i in order if scores[i] != float("-inf")]

def rank_items_in_memory(
    *,
    embedder: EmbeddingProvider,
    items: Sequence[Any],
    query: str,
    stringify=default_stringify,
    length_threshold: int = 180,   # kept for API symmetry
    top_k: Optional[int] = None,
    return_scores: bool = False,
):
    """
    Rank items by computing embeddings on the fly (NO DB).
    """
    _, texts = make_keys_for_items(items, stringify, length_threshold)
    doc_vecs = embedder.embed(texts, normalize=True)
    q_vec = embedder.embed([query], normalize=True)[0]
    scores: List[float] = [dot(v, q_vec) for v in doc_vecs]
    order = sorted(range(len(items)), key=lambda i: scores[i], reverse=True)
    if top_k is not None:
        order = order[:top_k]
    if return_scores:
        return [(items[i], scores[i]) for i in order]
    return [items[i] for i in order]

def ensure_embeddings_for_items(
    *,
    conn: sqlite3.Connection,
    embedder: EmbeddingProvider,
    items: Sequence[Any],
    stringify=default_stringify,
    length_threshold: int = 180,
) -> int:
    """
    Ensures embeddings exist in DB for the given items (for the active provider/stringify/threshold).
    Only creates missing ones. Returns the number of inserted entries.
    """
    model_id, _ = ensure_model(conn, embedder)
    keys, texts = make_keys_for_items(items, stringify, length_threshold)
    doc_mat, found, _ = load_vectors_for_keys(conn, model_id, keys)
    missing_idx = [i for i, ok in enumerate(found) if not ok]
    if not missing_idx:
        logger.debug("[json_rag][DB] all embeddings present; no backfill needed.")
        return 0

    # Debug: show some missing keys
    preview = [keys[i] for i in missing_idx[:5]]
    logger.debug(f"[json_rag][DB] backfilling {len(missing_idx)} missing embeddings … (examples: {preview})")

    # Embed only the missing ones
    to_texts = [texts[i] for i in missing_idx]
    embs = embedder.embed(to_texts, normalize=True)

    # Upsert pairs (key, vector) in the right order
    pairs = [(keys[i], embs[j]) for j, i in enumerate(missing_idx)]
    upsert_embeddings(conn, model_id, pairs)
    return len(pairs)
