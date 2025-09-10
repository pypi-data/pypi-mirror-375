# providers/langgraph_adapter.py
from __future__ import annotations

import json
import warnings
from typing import Any, Dict, List, Optional, Union

from .. import RunResponse, ProviderAdapter, OutputType, OpenAIMessage

# --- core deps (soft import with friendly error) ------------------------------
try:
    from langgraph.prebuilt import create_react_agent
    from langchain_openai import ChatOpenAI
    from langchain_core.tools import Tool
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
    _HAS_LG = True
except Exception:
    _HAS_LG = False

# pydantic for structured output (optional)
try:
    from pydantic import BaseModel as PydBaseModel
    _HAS_PYD = True
except Exception:
    PydBaseModel = object  # type: ignore
    _HAS_PYD = False

# jsonschema validation (optional)
try:
    from jsonschema import Draft202012Validator
    _HAS_JSONSCHEMA = True
except Exception:
    Draft202012Validator = None  # type: ignore
    _HAS_JSONSCHEMA = False

# langchain-mcp-adapters (optional)
try:
    from langchain_mcp_adapters import load_tools_from_mcp_servers  # type: ignore
    _HAS_LC_MCP = True
    _MCP_API = "batch"
except Exception:
    try:
        from langchain_mcp_adapters import load_mcp_tools  # type: ignore
        _HAS_LC_MCP = True
        _MCP_API = "single"
    except Exception:
        _HAS_LC_MCP = False
        _MCP_API = None


# put this near the top of providers/langgraph_adapter.py
from typing import Tuple

def _normalize_structured_output_spec(output_type: Any) -> Tuple[Any, str]:
    """
    Returns (spec, kind) where:
      kind in {"pydantic", "openai_function", "json_schema"}
    Accepted forms for LangChain:
      - Pydantic BaseModel (class or instance)
      - OpenAI function dict: {"name","description","parameters":{...json schema...}}
      - JSON Schema dict with top-level "title" and "description"
    If dict is a plain JSON schema missing title/description, we inject safe defaults.
    """
    # Pydantic?
    try:
        from pydantic import BaseModel as PydBaseModel  # local import in case not installed
        if isinstance(output_type, type) and issubclass(output_type, PydBaseModel):
            return output_type, "pydantic"
        if isinstance(output_type, PydBaseModel):
            return type(output_type), "pydantic"  # pass the class; LC prefers class
    except Exception:
        pass

    # Dict?
    if isinstance(output_type, dict):
        # OpenAI function format?
        if "parameters" in output_type and "name" in output_type:
            # Ensure description is present (required)
            if "description" not in output_type:
                output_type = {**output_type, "description": "Structured function output."}
            return output_type, "openai_function"

        # Plain JSON Schema – ensure top-level title/description exist
        schema = dict(output_type)  # shallow copy
        if "title" not in schema:
            schema["title"] = "StructuredOutput"
        if "description" not in schema:
            schema["description"] = "Structured JSON output."
        # ensure object type if missing
        if "type" not in schema:
            schema["type"] = "object"
        return schema, "json_schema"

    # Anything else is invalid for structured binding
    raise TypeError(
        "output_type must be a Pydantic BaseModel, an OpenAI function dict, or a JSON schema dict."
    )

def _require_deps():
    if not _HAS_LG:
        raise ImportError(
            "LangGraph adapter requires: langgraph, langchain, langchain-openai.\n"
            "Install with: pip install langgraph langchain langchain-openai"
        )


# ---------- message helpers ---------------------------------------------------

def _flatten_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if not isinstance(item, dict):
                parts.append(str(item)); continue
            t = item.get("type")
            if t in ("text", "input_text"):
                parts.append(item.get("text", ""))
            elif t in ("image_url", "input_image"):
                url = item.get("image_url") or item.get("url") or ""
                if isinstance(url, dict):
                    url = url.get("url", "")
                if url:
                    parts.append(f"[image: {url}]")
            elif t in ("file_url", "input_file"):
                url = item.get("file_url") or item.get("url") or ""
                if isinstance(url, dict):
                    url = url.get("url", "")
                if url:
                    parts.append(f"[file: {url}]")
            else:
                parts.append(str(item))
        return "\n".join(p for p in parts if p)
    return str(content)


def _oa_to_lc_messages(
    system_prompt: Optional[str],
    history: Optional[List[OpenAIMessage]],
    final_user: OpenAIMessage,
) -> List[Any]:
    msgs: List[Any] = []
    if system_prompt:
        msgs.append(SystemMessage(content=system_prompt))

    for m in (history or []):
        role = m.get("role")
        c = m.get("content", "")
        if role == "system":
            msgs.insert(0, SystemMessage(content=_flatten_content_to_text(c)))
        elif role == "user":
            msgs.append(HumanMessage(content=_flatten_content_to_text(c)))
        elif role == "assistant":
            msgs.append(AIMessage(content=_flatten_content_to_text(c)))
        elif role == "tool":
            msgs.append(ToolMessage(content=str(c), tool_call_id=m.get("tool_call_id", "")))
        else:
            msgs.append(HumanMessage(content=str(m)))

    msgs.append(HumanMessage(content=_flatten_content_to_text(final_user.get("content", ""))))
    return msgs


# ---------- output parsing helpers -------------------------------------------

def _parse_json_schema(text: str, schema: Dict[str, Any]) -> Any:
    try:
        obj = json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            obj = json.loads(text[start:end+1])
        else:
            raise ValueError(f"Model output is not valid JSON.\n{text}")
    if _HAS_JSONSCHEMA and Draft202012Validator is not None:
        v = Draft202012Validator(schema)
        errs = list(v.iter_errors(obj))
        if errs:
            e = errs[0]
            path = list(e.absolute_path)
            raise ValueError(f"JSON does not match schema at {path}: {e.message}")
    return obj


# ---------- MCP integration loader -------------------------------------------

def _load_mcp_tools_from_config(mcp_servers: Optional[List[Dict[str, Any]]]) -> List[Tool]:
    if not mcp_servers:
        return []
    if not _HAS_LC_MCP:
        warnings.warn(
            "MCP servers were provided, but 'langchain-mcp-adapters' is not installed. "
            "Install with: pip install langchain-mcp-adapters",
            RuntimeWarning,
        )
        return []

    tools: List[Tool] = []
    normalized: List[Dict[str, Any]] = []
    for i, s in enumerate(mcp_servers):
        if not isinstance(s, dict):
            warnings.warn(f"Ignoring MCP server entry #{i}: expected dict, got {type(s)}", RuntimeWarning)
            continue
        url = (s.get("href") or s.get("url") or "").strip()
        if not url:
            warnings.warn(f"Ignoring MCP server entry #{i}: missing 'url'/'href'", RuntimeWarning)
            continue
        headers = s.get("headers")
        name = s.get("name")
        normalized.append({"url": url, "headers": headers, "name": name})

    if not normalized:
        return []

    try:
        if _MCP_API == "batch":
            batch_tools = load_tools_from_mcp_servers(normalized)  # type: ignore
            tools.extend(batch_tools or [])
        elif _MCP_API == "single":
            for ent in normalized:
                single_tools = load_mcp_tools(ent["url"], headers=ent.get("headers"), name=ent.get("name"))  # type: ignore
                tools.extend(single_tools or [])
        else:
            warnings.warn("Unknown MCP adapter API; no MCP tools loaded.", RuntimeWarning)
    except Exception as e:
        warnings.warn(f"Failed to load MCP tools: {e}", RuntimeWarning)

    return tools


# ---------- adapter -----------------------------------------------------------

class LangGraphAdapter(ProviderAdapter):
    def __init__(self, config: Dict[str, Any]):
        """
        config:
          - model_name (str): default "gpt-4o-mini"
          - temperature (float): default 0
          - model_kwargs (dict): passed to ChatOpenAI
          - tool_choice (str): "auto" | "required" (default "auto")
        """
        self.config = dict(config or {})

    @classmethod
    def is_valid_config(cls, config: Optional[Dict[str, Any]] = None) -> bool:
        cfg = config or {}
        return True

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
    ) -> RunResponse:

        # ---- Shortcut: no LLM call if user passed custom_output_text ----
        if "custom_output_text" in kwargs:
            output = kwargs["custom_output_text"]
            mh = message_history or []
            filtered_hist = [m for m in mh if isinstance(m, dict) and m.get("role") != "system"]
            all_messages = []
            all_messages.extend(filtered_hist)
            all_messages.append({"role": "user", "content": input_text})
            all_messages.append({"role": "assistant", "content": output})
            return RunResponse(output=output, all_messages=all_messages)

        _require_deps()

        # Build synthetic user message
        content_blocks: List[Dict[str, Any]] = [{"type": "input_text", "text": input_text}]
        for img in images or []:
            src = img.get("src")
            if src:
                content_blocks.append({"type": "input_image", "image_url": src})
        for l in links or []:
            href = l.get("href")
            if href:
                content_blocks.append({"type": "input_file", "file_url": href})
        user_msg: OpenAIMessage = {"role": "user", "content": content_blocks}

        lc_messages = _oa_to_lc_messages(system_prompt, message_history, user_msg)

        # Model
        model_name = self.config.get("model_name") or self.config.get("model") or "gpt-4o-mini"
        temperature = float(self.config.get("temperature", 0))
        model_kwargs = dict(self.config.get("model_kwargs") or {})
        base_llm = ChatOpenAI(model=model_name, temperature=temperature, **model_kwargs)

        # User tools + MCP tools
        lc_tools: List[Tool] = []
        if tools:
            for t in tools:
                if isinstance(t, Tool):
                    lc_tools.append(t)
                elif isinstance(t, dict) and callable(t.get("callable")):
                    lc_tools.append(
                        Tool(
                            name=t.get("name") or t["callable"].__name__,
                            description=t.get("description", "No description."),
                            func=t["callable"],
                        )
                    )
                else:
                    warnings.warn(f"Unsupported tool format for LangGraph adapter: {type(t)}", RuntimeWarning)
        lc_tools.extend(_load_mcp_tools_from_config(mcp_servers))

        # ====== Structured output path (NO tools) – pass output_type to LLM ======
        if output_type is not None and not lc_tools:
            try:
                spec, kind = _normalize_structured_output_spec(output_type)
                llm_struct = base_llm.with_structured_output(spec)
                # Call the LLM directly with LangChain messages
                result_obj = await llm_struct.ainvoke(lc_messages)
                output = result_obj  # already structured (Pydantic instance or dict)
                # For all_messages, render a compact string version
                try:
                    final_text = result_obj.model_dump_json()  # pydantic v2
                except Exception:
                    final_text = json.dumps(result_obj, ensure_ascii=False)
            except Exception as e:
                warnings.warn(
                    f"with_structured_output failed ({e}); falling back to text + post-parse.",
                    RuntimeWarning,
                )
                # Fallback: plain call + post-parse
                resp = await base_llm.ainvoke(lc_messages)
                final_text = resp.content or ""
                if isinstance(output_type, dict):
                    try:
                        output = _parse_json_schema(final_text, output_type)
                    except Exception:
                        output = final_text
                elif _HAS_PYD and (
                    isinstance(output_type, PydBaseModel)
                    or (isinstance(output_type, type) and issubclass(output_type, PydBaseModel))
                ):
                    try:
                        data = json.loads(final_text)
                        model_cls = output_type if isinstance(output_type, type) else type(output_type)
                        output = model_cls.model_validate(data)
                    except Exception:
                        output = final_text
                else:
                    output = final_text

            # Build all_messages for this direct-call path
            all_messages: List[Dict[str, Any]] = []
            for m in lc_messages:
                if isinstance(m, SystemMessage):
                    all_messages.append({"role": "system", "content": m.content})
                elif isinstance(m, HumanMessage):
                    all_messages.append({"role": "user", "content": m.content})
            all_messages.append({"role": "assistant", "content": final_text})
            return RunResponse(output=output, all_messages=all_messages)


        # ====== Agent path (tools and/or no output_type) ======
        app = create_react_agent(base_llm, tools=lc_tools)
        init_state = {"messages": lc_messages}
        result = await app.ainvoke(init_state)
        msgs_out: List[Any] = result.get("messages", [])

        # Pull final assistant text
        final_text = ""
        for m in reversed(msgs_out):
            if isinstance(m, AIMessage):
                final_text = m.content or ""
                break

        # If output_type exists here, we must post-parse (agent doesn’t accept structured binding)
        if isinstance(output_type, dict):
            try:
                output = _parse_json_schema(final_text, output_type)
            except Exception:
                output = final_text
        elif _HAS_PYD and (
            isinstance(output_type, PydBaseModel)
            or (isinstance(output_type, type) and issubclass(output_type, PydBaseModel))
        ):
            try:
                data = json.loads(final_text)
                model_cls = output_type if isinstance(output_type, type) else type(output_type)
                output = model_cls.model_validate(data)
            except Exception:
                output = final_text
        else:
            output = final_text

        # Build OpenAI-style all_messages
        all_messages: List[Dict[str, Any]] = []
        for m in msgs_out:
            if isinstance(m, SystemMessage):
                all_messages.append({"role": "system", "content": m.content})
            elif isinstance(m, HumanMessage):
                all_messages.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                all_messages.append({"role": "assistant", "content": m.content})
            elif isinstance(m, ToolMessage):
                all_messages.append({"role": "tool", "content": m.content, "tool_call_id": getattr(m, "tool_call_id", "")})
            else:
                all_messages.append({"role": "assistant", "content": str(m)})

        if all_messages and all_messages[-1]["role"] == "assistant" and not isinstance(output, str):
            all_messages[-1]["content"] = json.dumps(output, ensure_ascii=False)

        return RunResponse(output=output, all_messages=all_messages)


def factory(config: Optional[Dict[str, Any]] = None) -> ProviderAdapter:
    return LangGraphAdapter(config or {})
