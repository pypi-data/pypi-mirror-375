from __future__ import annotations
import json
from hashlib import blake2b
from typing import Any, Callable, Sequence, Tuple, List

Stringifier = Callable[[Any], str]

def default_stringify(obj: Any) -> str:
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return str(obj)

def text_to_key(text: str, length_threshold: int) -> str:
    if len(text) <= length_threshold:
        return text
    return blake2b(text.encode("utf-8"), digest_size=20).hexdigest()

def make_keys_for_items(
    items: Sequence[Any],
    stringify: Stringifier,
    length_threshold: int,
) -> Tuple[List[str], List[str]]:
    texts = [stringify(x) for x in items]
    keys = [text_to_key(t, length_threshold) for t in texts]
    return keys, texts

def dot(a: List[float], b: List[float]) -> float:
    return sum(x*y for x,y in zip(a,b))

def _make_stringify_from_attrs(attrs: dict, default_sf: Stringifier) -> Stringifier:
    """
    Supports:
      - attrs["rag_key"]: str | list[str]  → stringify only those fields
      - attrs["rag_joiner"]: join string (default: " | ")
    """
    rag_key = attrs.get("rag_key")
    joiner = attrs.get("rag_joiner", " | ")

    if rag_key is None:
        return default_sf

    if isinstance(rag_key, str):
        keys = [rag_key]
    elif isinstance(rag_key, (list, tuple)):
        keys = list(rag_key)
    else:
        return default_sf

    def sf(obj: Any) -> str:
        if isinstance(obj, dict):
            parts = []
            for k in keys:
                v = obj.get(k, "")
                if isinstance(v, (list, tuple)):
                    parts.append(" ".join(map(str, v)))
                else:
                    parts.append(str(v))
            return joiner.join(parts).strip()
        return default_sf(obj)

    return sf
