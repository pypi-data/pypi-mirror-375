from __future__ import annotations
import json, warnings, logging
from typing import Any, Dict, List, Optional, Callable
from contextlib import AsyncExitStack
from openai import AsyncOpenAI

from botmark.runners import RunResponse, OutputType
from ...client import resolve_client, ClientContext
from ...messages import UserMessageBuilder, to_responses_parts
from ...tools import normalize_tools
from ...schema import JsonSchemaOutputValidator

from .computer import Computer
from .default import LocalPlaywrightBrowser
from .desktop import LocalPyAutoGuiDesktop

# ----------------------------
# Global state
# ----------------------------
import asyncio
from concurrent.futures import ThreadPoolExecutor

computer: Optional[Computer] = None
_computer_lock = asyncio.Lock()
_executor: Optional[ThreadPoolExecutor] = None

logger = logging.getLogger(__name__)

# async def get_computer( config: dict) -> Computer:
#     """
#     Ensure there is a single global LocalPlaywrightBrowser instance,
#     created and __enter__'d on the dedicated thread.
#     """
#     computer_use = config.get( "computer_use", {})
#     start_url = computer_use.get("start_url", "https://www.google.com/")
#     headless = computer_use.get("headless", False)

#     global computer
#     async with _computer_lock:
#         if computer is None:
#             def _init():
#                 comp = LocalPlaywrightBrowser(headless=headless, start_url=start_url)
#                 comp.__enter__()  # enter context on the same thread
#                 return comp
#             computer = await _on_computer_thread(_init)
#     return computer

async def get_computer(config: dict) -> Computer:
    """
    Ensure a single global Computer instance, created and __enter__'d on the dedicated thread.
    Use Playwright browser by default; switch to pyautogui desktop with computer_use.mode='desktop'
    (or an OS label: 'windows' | 'mac' | 'ubuntu').
    """
    computer_use = config.get("computer_use", {})
    mode = (computer_use.get("environment") or "").strip().lower() or None

    # Browser defaults
    start_url = computer_use.get("start_url", "https://www.google.com/")
    headless = bool(computer_use.get("headless", False))

    # Decide which Computer to build
    def _builder():
        nonlocal mode

        if mode == "browser":
            comp = LocalPlaywrightBrowser(headless=headless, start_url=start_url)
        else:
            comp = LocalPyAutoGuiDesktop( mode )
        comp.__enter__()
        return comp

    global computer
    async with _computer_lock:
        if computer is None:
            computer = await _on_computer_thread(_builder)
    return computer

def _ensure_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="computer-thread")
    return _executor

async def _on_computer_thread(fn: Callable[..., Any], *args, **kwargs):
    """Run a callable on the dedicated 'computer-thread'."""
    loop = asyncio.get_running_loop()
    executor = _ensure_executor()
    return await loop.run_in_executor(executor, lambda: fn(*args, **kwargs))

# ----------------------------
# OpenAI (async) call
# ----------------------------
async def create_response(**kwargs) -> Dict[str, Any]:
    client = AsyncOpenAI()
    try:
        resp = await client.responses.create(**kwargs)
        return resp.to_dict()
    except Exception as e:
        logger.debug(f"Error calling OpenAI Responses API: {e}")
        return {"error": str(e)}

class ComputerUsePreviewProcessor:
    """
    Standard Responses API path (tools, MCP, optional JSON schema) — with local computer loop.
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

        # ---------- computer-use setup ----------

        comp = await get_computer(self.config)
        dimensions = await _on_computer_thread(comp.get_dimensions)
        env = await _on_computer_thread(comp.get_environment)
        computer_use_tools = [{
            "type": "computer-preview",
            "display_width": dimensions[0],
            "display_height": dimensions[1],
            "environment": env,
        }]

        client = resolve_client(self.config)
        if client is None:
            raise RuntimeError("No valid configuration for OpenAI or Azure found!")

        async with AsyncExitStack() as stack:
            await stack.enter_async_context(ClientContext(client))

            # ---------- Build base messages ----------
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

            # ---------- Tools (local + MCP) ----------
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

            # ---------- Structured outputs (optional) ----------
            response_format = None
            output_validator = None
            json_schema_system_hint = None

            if isinstance(output_type, dict):
                response_format = {
                    "type": "json_schema",
                    "json_schema": {"name": "Schema", "schema": output_type, "strict": True}
                }
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

            # ---------- Model & params ----------
            model = self.config.get("model") or kwargs.pop("model", None)
            if not model:
                warnings.warn("No model specified; relying on server default.", RuntimeWarning)

            allowed_resp_params = {
                "temperature", "top_p", "max_output_tokens", "stop",
                "frequency_penalty", "presence_penalty", "seed", "user", "timeout", "metadata"
            }

            resp_kwargs = {k: v for k, v in kwargs.items() if k in allowed_resp_params}
            resp_kwargs["truncation"] = self.config.get("truncation", "auto")
            resp_kwargs["reasoning"] = self.config.get("reasoning", { "summary": "concise" })

            async def _responses_create_with_optional_schema(items: List[Dict[str, Any]], use_tools: List[Dict[str, Any]]):
                """
                Call Responses API, handling optional JSON schema and the MCP/local tool `requires_action` loop.
                Returns the final response object whose dict contains "output" (i.e., not requires_action anymore).
                """
                # First attempt (with response_format if present)
                async def _create_once():
                    if response_format is not None:
                        try:
                            return await client.responses.create(
                                model=model,
                                input=items,
                                tools=use_tools if use_tools else None,
                                response_format=response_format,
                                **resp_kwargs,
                            )
                        except TypeError:
                            # Model may not support response_format; fall back with a system hint.
                            if json_schema_system_hint:
                                items.insert(0, {"role": "system", "content": to_responses_parts("system", json_schema_system_hint)})
                    return await client.responses.create(
                        model=model,
                        input=items,
                        tools=use_tools if use_tools else None,
                        **resp_kwargs,
                    )

                resp_obj = await _create_once()

                # Handle local tool calls (requires_action → submit_tool_outputs)
                while getattr(resp_obj, "status", None) == "requires_action":
                    required = getattr(resp_obj, "required_action", None) or {}
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

                    resp_obj = await client.responses.submit_tool_outputs(
                        response_id=resp_obj.id, tool_outputs=tool_outputs
                    )

                return resp_obj

            # ---------- Helper to stringify message content ----------
            def _as_string_content(m: Dict[str, Any]) -> str:
                c = m.get("content")
                if isinstance(c, str): 
                    return c
                if isinstance(c, list):
                    parts = []
                    for item in c:
                        t = item.get("type")
                        if t in ("input_text", "output_text"):
                            parts.append(item.get("text", ""))
                        elif t == "input_image":
                            parts.append(f"[image: {item.get('image_url','')}]")
                        elif t == "input_file":
                            if "file_id" in item: parts.append(f"[file_id: {item['file_id']}]")
                            elif "file_url" in item: parts.append(f"[file_url: {item['file_url']}]")
                    return "\n".join([p for p in parts if p])
                return str(c)

            # ---------- Interactive computer-use loop ----------
            items: List[Dict[str, Any]] = list(input_messages)  # working transcript
            combined_tools = (tools_out or []) + computer_use_tools
            last_resp_dict: Dict[str, Any] = {}

            while True:
                resp_obj = await _responses_create_with_optional_schema(items, combined_tools)
                # Safely get a dict view
                resp_dict = resp_obj.to_dict() if hasattr(resp_obj, "to_dict") else dict(resp_obj or {})
                last_resp_dict = resp_dict

                # If we got an 'output' list, process it (messages + computer calls)
                output_list: List[Dict[str, Any]] = resp_dict.get("output") or []
                if not output_list:
                    # Fallback: no structured output. Stop here.
                    break

                # Append model outputs to the transcript
                items.extend(output_list)

                # Execute any computer calls and append their outputs
                for out_item in output_list:
                    if out_item.get("type") != "computer_call":
                        continue

                    action = out_item.get("action") or {}
                    action_type = action.get("type")
                    action_args = {k: v for k, v in action.items() if k != "type"}

                    # (Optional) honor pending safety checks by auto-acknowledging them here.
                    pending_checks = out_item.get("pending_safety_checks", []) or []

                    # Perform the action on the dedicated thread
                    await _on_computer_thread(getattr(comp, action_type), **action_args)

                    # Screenshot on the same thread
                    screenshot_base64 = await _on_computer_thread(comp.screenshot)

                    call_output: Dict[str, Any] = {
                        "type": "computer_call_output",
                        "call_id": out_item.get("call_id"),
                        "acknowledged_safety_checks": pending_checks,
                        "output": {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{screenshot_base64}",
                        },
                    }

                    # Add current_url for browser envs
                    current_env = await _on_computer_thread(comp.get_environment)
                    if current_env == "browser":
                        current_url = await _on_computer_thread(comp.get_current_url)
                        call_output["output"]["current_url"] = current_url

                    items.append(call_output)

                # Stop once the last item is a terminal assistant message
                if items and items[-1].get("role") == "assistant":
                    break

            # ---------- Finalize output ----------
            # Prefer SDK's output_text; otherwise read from last assistant message.
            final_text = getattr(resp_obj, "output_text", None) if 'resp_obj' in locals() else None
            if not final_text:
                # Find last assistant message in the transcript
                for m in reversed(items):
                    if m.get("role") == "assistant":
                        final_text = _as_string_content(m)
                        break
            final_text = final_text or ""

            if output_validator is not None and final_text:
                output_validator.validate(final_text)

            # Produce a simplified chat log (strings only) for downstream consumers.
            def _flatten_to_simple(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                simple: List[Dict[str, Any]] = []
                for m in messages:
                    role = m.get("role", "user")
                    if role not in ("system", "user", "assistant"):
                        # skip non-chat artifacts like computer_call(_output)
                        continue
                    simple.append({"role": role, "content": _as_string_content(m)})
                return simple

            simple_messages = _flatten_to_simple(items) or [
                *(_flatten_to_simple(input_messages)),
                {"role": "assistant", "content": final_text},
            ]

            return RunResponse(output=final_text, all_messages=simple_messages)
