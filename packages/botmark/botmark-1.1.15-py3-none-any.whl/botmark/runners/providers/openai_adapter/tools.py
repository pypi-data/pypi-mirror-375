from __future__ import annotations
import ast, inspect
from typing import Any, Dict, List, Tuple, Callable

def _compile_top_level_function(code_str: str) -> Tuple[Callable[..., Any], str]:
    module = ast.parse(code_str)
    func_names = [n.name for n in module.body if isinstance(n, ast.FunctionDef)]
    if not func_names:
        raise ValueError("Tool code must contain at least one top-level function (def ...).")
    ns: Dict[str, Any] = {}
    exec(code_str, ns, ns)
    fn = ns.get(func_names[0])
    if not callable(fn):
        raise TypeError("Compiled object is not callable.")
    return fn, func_names[0]

def _infer_parameters_schema_from_signature(fn: Callable[..., Any]) -> Dict[str, Any]:
    sig = inspect.signature(fn)
    props: Dict[str, Any] = {}
    required: List[str] = []

    def _map(py: Any) -> Dict[str, Any]:
        if py in (int, "int"): return {"type": "integer"}
        if py in (float, "float"): return {"type": "number"}
        if py in (bool, "bool"): return {"type": "boolean"}
        if py in (list, "list"): return {"type": "array"}
        if py in (dict, "dict"): return {"type": "object"}
        return {"type": "string"}

    for name, param in sig.parameters.items():
        if name.startswith("_"): continue
        ann = param.annotation if param.annotation is not inspect._empty else str
        schema = _map(ann)
        if param.default is inspect._empty:
            required.append(name)
        props[name] = {"description": f"Parameter '{name}'", **schema}

    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}

def toolspecs_to_openai_tools_and_registry(toolspecs: List[Dict[str, Any]]):
    openai_tools: List[Dict[str, Any]] = []
    registry: Dict[str, Callable[..., Any]] = {}

    for i, spec in enumerate(toolspecs):
        if not isinstance(spec, dict) or "code" not in spec:
            raise TypeError(f"Tool #{i} must be a dict with a 'code' key.")
        fn, discovered_name = _compile_top_level_function(spec["code"])
        attrs = (spec.get("attributes") or {})
        name = (attrs.get("id") or discovered_name).strip()
        if not name:
            raise ValueError(f"Tool #{i} has no name.")
        try:
            fn.__name__ = name
        except Exception:
            pass
        description = attrs.get("description") or (fn.__doc__ or "").strip() or f"Tool '{name}'."
        params_schema = attrs.get("parameters") or _infer_parameters_schema_from_signature(fn)

        # Responses API shape: top-level name/description/parameters
        openai_tools.append({
            "type": "function",
            "name": name,
            "description": description,
            "parameters": params_schema,
        })
        registry[name] = fn

    return openai_tools, registry

def normalize_tools(tools_in: Any):
    """
    Accepts:
      - [{'code': str, 'attributes': {...}}, ...]
      - {name: (callable, schema?|None, description?)} mapping
      - list[callable] or single callable
    Returns (openai_tools, registry)
    """
    if tools_in is None:
        return None, {}

    if isinstance(tools_in, list) and tools_in and isinstance(tools_in[0], dict) and "code" in tools_in[0]:
        return toolspecs_to_openai_tools_and_registry(tools_in)

    if isinstance(tools_in, dict) and tools_in:
        openai_tools: List[Dict[str, Any]] = []
        registry: Dict[str, Callable[..., Any]] = {}
        for name, val in tools_in.items():
            if isinstance(val, (tuple, list)):
                fn = val[0]
                params = (val[1] if len(val) > 1 and isinstance(val[1], dict) else None)
                desc = (val[2] if len(val) > 2 and isinstance(val[2], str) else None)
            else:
                fn, params, desc = val, None, None
            if not params:
                params = _infer_parameters_schema_from_signature(fn)
            if not desc:
                desc = (fn.__doc__ or "").strip() or f"Tool '{name}'."
            try:
                fn.__name__ = name
            except Exception:
                pass

            # Responses API shape
            openai_tools.append({
                "type": "function",
                "name": name,
                "description": desc,
                "parameters": params,
            })
            registry[name] = fn
        return openai_tools, registry

    if isinstance(tools_in, list) and all(callable(x) for x in tools_in):
        mapped = [{"code": inspect.getsource(fn), "attributes": {"id": fn.__name__, "description": (fn.__doc__ or "").strip()}} for fn in tools_in]
        return toolspecs_to_openai_tools_and_registry(mapped)

    if callable(tools_in):
        return toolspecs_to_openai_tools_and_registry(
            [{"code": inspect.getsource(tools_in), "attributes": {"id": tools_in.__name__, "description": (tools_in.__doc__ or "").strip()}}]
        )

    raise TypeError("Unsupported tools type.")
