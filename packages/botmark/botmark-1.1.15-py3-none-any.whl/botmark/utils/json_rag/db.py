from __future__ import annotations
import os, json, sqlite3
from typing import Tuple, Dict, Any, List

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS models (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tag TEXT NOT NULL UNIQUE,
  provider TEXT NOT NULL,
  name TEXT NOT NULL,
  dim INTEGER NOT NULL,
  normalized INTEGER NOT NULL,
  probe_vec TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS embeddings (
  model_id INTEGER NOT NULL,
  doc_key  TEXT NOT NULL,
  vec      TEXT NOT NULL,
  meta_json TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (model_id, doc_key),
  FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(model_id);
"""

def open_db(path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys=ON")
    for stmt in SCHEMA.strip().split(";"):
        s = stmt.strip()
        if s:
            conn.execute(s)
    conn.commit()
    return conn

def _provider_from_tag(tag: str) -> str:
    return tag.split("/")[0] if "/" in tag else tag

def _name_from_tag(tag: str) -> str:
    return "/".join(tag.split("/")[1:]) if "/" in tag else tag

def _cosine_is_close(a: list[float], b: list[float], tol: float=1e-3) -> bool:
    dot = sum(x*y for x,y in zip(a,b))
    return dot >= 1.0 - tol

def ensure_model(conn: sqlite3.Connection, embedder) -> Tuple[int, Dict[str, Any]]:
    cur = conn.cursor()
    tag = embedder.tag
    probe_text = "__MODEL_PROBE_v1__"
    probe_vec = embedder.embed([probe_text], normalize=True)[0]
    dim = len(probe_vec)
    normalized = 1
    row = cur.execute("SELECT id, dim, normalized, probe_vec FROM models WHERE tag=?", (tag,)).fetchone()
    if row:
        mid, dim_db, norm_db, probe_db_json = row
        if int(dim_db)!=dim or int(norm_db)!=normalized:
            raise ValueError("Model mismatch (dim/norm).")
        probe_db = json.loads(probe_db_json)
        if _cosine_is_close(probe_db, probe_vec):
            return mid, {"tag": tag, "dim": dim, "normalized": True}
        else:
            raise ValueError("Probe embedding mismatch – different model/revision?")
    cur.execute(
        "INSERT INTO models(tag, provider, name, dim, normalized, probe_vec) VALUES(?,?,?,?,?,?)",
        (tag, _provider_from_tag(tag), _name_from_tag(tag), dim, normalized, json.dumps(probe_vec)),
    )
    conn.commit()
    return cur.lastrowid, {"tag": tag, "dim": dim, "normalized": True}

def upsert_embeddings(conn: sqlite3.Connection, model_id:int, pairs: list[tuple[str,list[float]]], metas: list[dict] | None = None):
    metas = metas or [{} for _ in pairs]
    if len(metas) != len(pairs):
        raise ValueError("metas must have same length as pairs.")
    cur = conn.cursor()
    for (doc_key, vec), meta in zip(pairs, metas):
        cur.execute("""
            INSERT INTO embeddings(model_id, doc_key, vec, meta_json)
            VALUES(?,?,?,?)
            ON CONFLICT(model_id, doc_key) DO UPDATE SET
              vec=excluded.vec, meta_json=excluded.meta_json
        """, (model_id, doc_key, json.dumps(vec), json.dumps(meta)))
    conn.commit()

def load_vectors_for_keys(conn: sqlite3.Connection, model_id:int, keys: list[str]) -> tuple[list[list[float]], list[bool], int]:
    cur = conn.cursor()
    row = cur.execute("SELECT dim FROM models WHERE id=?", (model_id,)).fetchone()
    if not row:
        raise ValueError("Unknown model_id.")
    dim = int(row[0])
    vecs: list[list[float]] = [[0.0]*dim for _ in keys]
    found = [False]*len(keys)
    for i,k in enumerate(keys):
        r = cur.execute("SELECT vec FROM embeddings WHERE model_id=? AND doc_key=?", (model_id,k)).fetchone()
        if r:
            vecs[i] = json.loads(r[0])
            found[i] = True
    return vecs, found, dim
