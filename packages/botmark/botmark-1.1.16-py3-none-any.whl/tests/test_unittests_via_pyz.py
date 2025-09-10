# tests/test_unittests_from_md_against_pyz.py
"""
Read `.unittest` blocks from the Markdown sources on disk
and run them against the corresponding models embedded in the built .pyz.

Flow
----
1) Locate `build.py` and the Markdown root: ../tests/unittests (relative to build.py)
2) Build a zipapp (.pyz) that embeds ALL models from that folder (recursive)
3) Import `app.gateway` **from the .pyz**
4) Parse `.unittest` blocks directly from the Markdown files on disk
5) For every parsed Q/A case, call:
       gateway.respond_sync({"model": <model_id>, "input": <question>})
   and assert the answer using:
     - exact equality
     - `regex: <pattern>`
     - `contains: <substring>`

Notes
-----
- Robust fence parser: supports both ~~~ and ``` fences, and detects `.unittest`
  in the attribute braces on the opening fence line (e.g. `{#id .unittest}`).
- Model IDs are derived exactly like build.py in recursive mode:
  relative path (without suffix) with "/" as separator.
- If NO unittest cases are found at all, the test is SKIPPED (not failed)
  but prints a clear summary of discovered models and tests.

Compatibility note with build.py outputs
----------------------------------------
Your build script may emit the zipapp either to the requested --dist/--name path
or adjacent to the provided markdown path (drag-and-drop UX). This test now:
  1) Prefers the requested --dist/--name path
  2) Falls back to <markdown_dir.parent>/<name>
  3) Parses a “Done: <path>” line from build.py stdout
"""

from __future__ import annotations
import os
import re
import sys
import shlex
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

import pytest


# ──────────────────────────────────────────────────────────────────────────────
# Path helpers
# ──────────────────────────────────────────────────────────────────────────────

def _find_build_py(start: Path) -> Path:
    """Find scripts/build.py (or build.py) walking upwards a few levels."""
    cand = (start / "../scripts/build.py").resolve()
    if cand.exists():
        return cand
    cur = start.resolve()
    for _ in range(5):
        p = (cur / "scripts/build.py").resolve()
        if p.exists():
            return p
        p2 = (cur / "build.py").resolve()
        if p2.exists():
            return p2
        cur = cur.parent
    raise FileNotFoundError("Could not locate build.py (searched ../scripts/build.py and up to 5 parents).")


def _markdown_root_from_build(build_py: Path) -> Path:
    """Per requirement: ../tests/unittests relative to build.py."""
    return (build_py.parent / "../tests/unittests").resolve()


def _expected_model_ids(markdown_root: Path) -> List[str]:
    """Model IDs like build.py (recursive): relative path w/o suffix, joined by '/'."""
    ids: List[str] = []
    for md in sorted(markdown_root.rglob("*.md")):
        rel = md.relative_to(markdown_root).with_suffix("")
        ids.append("/".join(rel.parts))
    return ids


# ──────────────────────────────────────────────────────────────────────────────
# Build .pyz (force UTF-8 logs for Windows)
# ──────────────────────────────────────────────────────────────────────────────

def _env_utf8() -> dict:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    # these help in some CI shells
    env.setdefault("LC_ALL", "C.UTF-8")
    env.setdefault("LANG", "C.UTF-8")
    return env


def _build_zipapp(build_py: Path, markdown_dir: Path, out_dir: Path, name: str) -> Path:
    """
    Build the .pyz with build.py. Primary expected output is out_dir/name,
    but support build.py variants that write next to the markdown path or
    print the final path via a 'Done:' line.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / name
    cmd = [
        sys.executable, "-X", "utf8",
        str(build_py),
        str(markdown_dir),
        "--recursive",
        "--dist", str(out_dir),
        "--name", name,
    ]
    print("BUILD:", " ".join(shlex.quote(str(x)) for x in cmd))
    # Capture stdout/stderr safely as UTF-8 (avoid UnicodeDecodeError on Windows)
    proc = subprocess.run(
        cmd,
        check=False,
        env=_env_utf8(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    if proc.returncode != 0:
        raise RuntimeError(f"build.py failed with exit code {proc.returncode}")

    # 1) Expected location if --dist/--name were honored
    if out_path.exists():
        return out_path

    # 2) Fallback: alongside the markdown folder (drag-and-drop UX)
    fallback1 = (markdown_dir.parent / name).resolve()
    if fallback1.exists():
        return fallback1

    # 3) Fallback: parse a 'Done: <path>' or '✅ Done: <path>' line
    for line in (proc.stdout or "").splitlines():
        s = line.strip()
        if s.startswith("✅ Done:") or s.startswith("Done:"):
            cand_text = s.split(":", 1)[-1].strip().strip("'\"")
            cand = Path(cand_text)
            if cand.exists():
                return cand

    raise AssertionError(f"Expected zipapp at {out_path}, and no fallback location was found.")


# ──────────────────────────────────────────────────────────────────────────────
# Import gateway from .pyz
# ──────────────────────────────────────────────────────────────────────────────

def _import_gateway(pyz_path: Path):
    sys.path.insert(0, str(pyz_path))
    try:
        import app.gateway as gateway  # type: ignore
    except Exception as e:
        raise RuntimeError(f"Failed to import app.gateway from {pyz_path}: {e}")
    return gateway


# ──────────────────────────────────────────────────────────────────────────────
# Markdown unittest parser
# ──────────────────────────────────────────────────────────────────────────────

FENCE_START_RE = re.compile(
    r"""^([`~]{3,})          # fence marker (``` or ~~~, 3+)
        \s*([a-zA-Z0-9_-]+)? # optional info string / language (e.g., markdown)
        [ \t]*               # spaces
        (\{[^}]*\})?         # optional attribute braces like {#id .unittest}
        [ \t]*$              # end line
    """,
    re.VERBOSE,
)

def _is_unittest_fence(info_str: str | None, attr_braces: str | None) -> bool:
    """Return True if opening fence declares a .unittest class in its braces."""
    if not attr_braces:
        return False
    return ".unittest" in attr_braces


def _extract_unittest_blocks(md_text: str) -> List[str]:
    lines = md_text.splitlines()
    blocks: List[str] = []
    i = 0
    while i < len(lines):
        m = FENCE_START_RE.match(lines[i])
        if not m:
            i += 1
            continue
        fence_marker, info, braces = m.group(1), m.group(2), m.group(3)
        is_ut = _is_unittest_fence(info, braces)
        i += 1
        content_lines: List[str] = []
        while i < len(lines):
            if lines[i].startswith(fence_marker):
                break
            content_lines.append(lines[i])
            i += 1
        if i < len(lines) and lines[i].startswith(fence_marker):
            i += 1
        if is_ut:
            blocks.append("\n".join(content_lines))
    return blocks


_Q_LINE = re.compile(r"^\s*#\s*(.+?)\s*$")
_A_LINE = re.compile(r"^\s*>\s*(.+?)\s*$")

def _parse_qa_pairs(block_text: str) -> List[Tuple[str, str]]:
    tests: List[Tuple[str, str]] = []
    cur_q: str | None = None
    for line in block_text.splitlines():
        if line.strip().startswith("<!--"):
            continue
        m_q = _Q_LINE.match(line)
        if m_q:
            cur_q = m_q.group(1).strip()
            continue
        m_a = _A_LINE.match(line)
        if m_a and cur_q:
            tests.append((cur_q, m_a.group(1).strip()))
            cur_q = None
    return tests


def _collect_tests_from_md(markdown_root: Path) -> Dict[str, List[Tuple[str, str]]]:
    result: Dict[str, List[Tuple[str, str]]] = {}
    for md in sorted(markdown_root.rglob("*.md")):
        model_id = "/".join(md.relative_to(markdown_root).with_suffix("").parts)
        text = md.read_text(encoding="utf-8")
        ut_blocks = _extract_unittest_blocks(text)
        pairs: List[Tuple[str, str]] = []
        for blk in ut_blocks:
            pairs.extend(_parse_qa_pairs(blk))
        if pairs:
            result[model_id] = pairs
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Assertions
# ──────────────────────────────────────────────────────────────────────────────

_RE_REGEX = re.compile(r"^\s*regex\s*:\s*(.+)$", re.I)
_RE_CONTAINS = re.compile(r"^\s*contains\s*:\s*(.+)$", re.I)

def _assert_expected(actual: str, expected: str):
    if m := _RE_REGEX.match(expected):
        pat = m.group(1).strip()
        assert re.search(pat, actual, flags=re.S), f"Regex not matched\nPATTERN: {pat}\nGOT:\n{actual}"
        return
    if m := _RE_CONTAINS.match(expected):
        sub = m.group(1).strip()
        assert sub in actual, f"Substring not found\nNEED: {sub}\nGOT:\n{actual}"
        return
    assert actual == expected, f"Expected {expected!r}, got {actual!r}"


# ──────────────────────────────────────────────────────────────────────────────
# The test
# ──────────────────────────────────────────────────────────────────────────────

def test_unittests_from_md_against_pyz(tmp_path: Path):
    here = Path(__file__).resolve().parent
    build_py = _find_build_py(here)
    md_root = _markdown_root_from_build(build_py)
    assert md_root.exists(), f"Markdown root not found: {md_root}"

    pyz = _build_zipapp(build_py, md_root, tmp_path, name="botmark_unittests.pyz")
    print(f"[PYZ] Built: {pyz}")

    gw = _import_gateway(pyz)

    expected_ids = set(_expected_model_ids(md_root))
    get_models = getattr(gw, "get_models", None)
    assert callable(get_models), "gateway.get_models() missing"
    info = get_models() or {}
    got_ids = {m.get("id") for m in (info.get("data") or []) if isinstance(m, dict)}
    print(f"[SMOKE] Models in .pyz: {sorted(got_ids)}")
    assert got_ids == expected_ids, "Model IDs in .pyz do not match disk"

    tests_by_model = _collect_tests_from_md(md_root)

    print("\n=== Unittest discovery (from Markdown on disk) ===")
    if tests_by_model:
        for mid, cases in tests_by_model.items():
            print(f" - {mid}: {len(cases)} case(s)")
    else:
        print(" - No `.unittest` cases found in any Markdown file.")
        pytest.skip("No `.unittest` cases present; skipping execution")
    print("=================================================\n")

    respond_sync = getattr(gw, "respond_sync", None)
    assert callable(respond_sync), "gateway.respond_sync(payload) missing"

    for model_id, cases in tests_by_model.items():
        for idx, (q, expected) in enumerate(cases, 1):
            payload = {"model": model_id, "messages": [{"role": "user", "content": q}]}
            try:
                result = respond_sync(payload)
            except Exception as e:
                pytest.fail(f"[{model_id}][#{idx}] respond_sync error: {e}")
            actual = result.get("output") if isinstance(result, dict) else str(result)
            actual = "" if actual is None else str(actual)
            print(f"[{model_id} Q{idx}] {q}\n -> {actual!r}")
            _assert_expected(actual.strip(), expected.strip())
