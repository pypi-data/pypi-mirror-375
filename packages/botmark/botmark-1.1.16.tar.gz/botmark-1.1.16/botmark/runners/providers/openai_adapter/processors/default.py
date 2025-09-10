from __future__ import annotations
import json, warnings
from typing import Any, Dict, List, Optional, Callable
from contextlib import AsyncExitStack

from botmark.runners import RunResponse, OutputType
from ..client import resolve_client, ClientContext
from ..messages import UserMessageBuilder, to_responses_parts
from ..tools import normalize_tools
from ..schema import JsonSchemaOutputValidator

class DefaultProcessor:
    """
    Standard Responses API path (tools, MCP, optional JSON schema) — no local computer loop.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = dict(config or {})

    async def run(
        self,
        *,
        input_text: str,
        message_history: Optional[List[Dict[str, Any]]],
        system_prompt: Optional[str],
        tools: Optional[Any],
        output_type: Optional[OutputType],
        mcp_servers: Optional[List[Dict[str, Any]]],
        links: Optional[List[Dict[str, Any]]],
        images: Optional[List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> RunResponse:

        # Early exit for custom output
        custom_output_text = kwargs.pop("custom_output_text", None)
        if custom_output_text is not None:
            mh = message_history or []
            filtered_hist = [m for m in mh if isinstance(m, dict) and m.get("role") != "system"]
            all_messages: List[Dict[str, Any]] = []
            all_messages.extend(filtered_hist)
            all_messages.append({"role": "user", "content": input_text})
            all_messages.append({"role": "assistant", "content": custom_output_text})
            return RunResponse(output=custom_output_text, all_messages=all_messages)

        client = resolve_client(self.config)
        if client is None:
            raise RuntimeError("No valid configuration for OpenAI or Azure found!")

        async with AsyncExitStack() as stack:
            await stack.enter_async_context(ClientContext(client))

            # Build messages
            system_text = (system_prompt or self.config.get("system_prompt") or "").strip()
            input_messages: List[Dict[str, Any]] = []
            if system_text:
                input_messages.append({"role": "system", "content": to_responses_parts("system", system_text)})

            mh = message_history or []
            if not isinstance(mh, list):
                raise TypeError("message_history must be a list of messages or None")
            for m in mh:
                if not isinstance(m, dict):
                    continue
                role = m.get("role")
                if role not in ("user", "assistant"):
                    continue
                parts = to_responses_parts(role, m.get("content"))
                if parts:
                    input_messages.append({"role": role, "content": parts})

            builder = UserMessageBuilder(prefer_upload=True)
            user_msg = builder.build_user_parts(
                user_text=input_text,
                images=[i.get("src") for i in images] if images else [],
                links=[l.get("href") for l in links] if links else [],
            )
            input_messages.append(user_msg)

            # Tools + MCP
            tools_out: List[Dict[str, Any]] = []
            tool_registry: Dict[str, Callable[..., Any]] = {}

            local_tools, tool_registry = normalize_tools(tools)
            if local_tools:
                tools_out.extend(local_tools)

            for idx, entry in enumerate(mcp_servers or []):
                if not isinstance(entry, dict):
                    continue
                url = (entry.get("url") or entry.get("href") or "").strip()
                if not url:
                    continue
                tools_out.append({
                    "type": "mcp",
                    "server_label": entry.get("name") or f"mcp_{idx+1}",
                    "server_description": entry.get("description") or f"MCP server {idx+1}",
                    "server_url": url,
                    "require_approval": entry.get("require_approval", "never"),
                    "allowed_tools": entry.get("allowed_tools") or None,
                })

            # Structured outputs
            response_format = None
            output_validator = None
            json_schema_system_hint = None

            if isinstance(output_type, dict):
                response_format = {"type": "json_schema", "json_schema": {"name": "Schema", "schema": output_type, "strict": True}}
                output_validator = JsonSchemaOutputValidator(output_type, strict=True)
                json_schema_system_hint = (
                    "You MUST respond ONLY with JSON that strictly conforms to this JSON Schema:\n"
                    + json.dumps(output_type, ensure_ascii=False)
                )
            elif output_type is not None:
                try:
                    from pydantic import BaseModel as PydBaseModel
                except ImportError:
                    raise ImportError("Install pydantic to use a BaseModel as output_type: pip install pydantic")
                if isinstance(output_type, type) and issubclass(output_type, PydBaseModel):
                    schema = output_type.model_json_schema()  # type: ignore[attr-defined]
                    response_format = {"type": "json_schema", "json_schema": {"name": "Schema", "schema": schema, "strict": True}}
                    output_validator = JsonSchemaOutputValidator(schema, strict=True)
                    json_schema_system_hint = (
                        "You MUST respond ONLY with JSON that strictly conforms to this JSON Schema:\n"
                        + json.dumps(schema, ensure_ascii=False)
                    )
                else:
                    raise TypeError("output_type must be a dict (JSON Schema) or a Pydantic BaseModel class.")

            # Model & params
            model = self.config.get("model") or kwargs.pop("model", None)
            if not model:
                warnings.warn("No model specified; relying on server default.", RuntimeWarning)

            allowed_resp_params = {
                "temperature", "top_p", "max_output_tokens", "stop",
                "frequency_penalty", "presence_penalty", "seed", "user", "timeout", "metadata"
            }
            resp_kwargs = {k: v for k, v in kwargs.items() if k in allowed_resp_params}

            async def _responses_create_with_optional_schema():
                if response_format is not None:
                    try:
                        return await client.responses.create(
                            model=model,
                            input=input_messages,
                            tools=tools_out if tools_out else None,
                            response_format=response_format,
                            **resp_kwargs,
                        )
                    except TypeError:
                        if json_schema_system_hint:
                            input_messages.insert(0, {"role": "system", "content": to_responses_parts("system", json_schema_system_hint)})
                return await client.responses.create(
                    model=model,
                    input=input_messages,
                    tools=tools_out if tools_out else None,
                    **resp_kwargs,
                )

            resp = await _responses_create_with_optional_schema()

            # Local python tool loop
            while getattr(resp, "status", None) == "requires_action":
                required = getattr(resp, "required_action", None) or {}
                if required.get("type") != "submit_tool_outputs":
                    break
                tool_calls = (required.get("submit_tool_outputs", {}) or {}).get("tool_calls", []) or []
                tool_outputs: List[Dict[str, str]] = []
                for call in tool_calls:
                    tc_id = call.get("id")
                    fn_info = (call.get("function") or {})
                    name = fn_info.get("name")
                    raw_args = fn_info.get("arguments") or "{}"
                    try:
                        args = json.loads(raw_args)
                    except Exception:
                        args = {}
                    fn = tool_registry.get(name or "")
                    if not fn:
                        out = {"error": f"Tool '{name}' not registered."}
                    else:
                        try:
                            out = fn(**args)
                        except Exception as e:
                            out = {"error": f"{type(e).__name__}: {e}"}
                    tool_outputs.append({"tool_call_id": tc_id, "output": json.dumps(out, ensure_ascii=False)})
                resp = await client.responses.submit_tool_outputs(response_id=resp.id, tool_outputs=tool_outputs)

            final_text = getattr(resp, "output_text", None) or ""

            if output_validator is not None and final_text:
                output_validator.validate(final_text or "")

            # flatten
            def _as_string_content(m: Dict[str, Any]) -> str:
                c = m.get("content")
                if isinstance(c, str): return c
                if isinstance(c, list):
                    parts = []
                    for item in c:
                        t = item.get("type")
                        if t in ("input_text", "output_text"): parts.append(item.get("text", ""))
                        elif t == "input_image": parts.append(f"[image: {item.get('image_url','')}]")
                        elif t == "input_file":
                            if "file_id" in item: parts.append(f"[file_id: {item['file_id']}]")
                            elif "file_url" in item: parts.append(f"[file_url: {item['file_url']}]")
                    return "\n".join([p for p in parts if p])
                return str(c)

            simple_messages: List[Dict[str, Any]] = []
            for m in input_messages:
                role = m.get("role", "user")
                simple_messages.append({"role": role, "content": _as_string_content(m)})
            simple_messages.append({"role": "assistant", "content": final_text})

            return RunResponse(output=final_text, all_messages=simple_messages)
