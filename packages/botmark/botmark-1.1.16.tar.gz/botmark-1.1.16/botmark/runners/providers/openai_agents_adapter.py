# providers/openai_agents_adapter.py
from __future__ import annotations
import inspect, json, os, mimetypes, base64, warnings
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional, Union, Tuple

from .. import RunResponse, ProviderAdapter, OutputType

# The OpenAI Agents SDK (pip install openai-agents)
try:
    from agents import Agent as OAAgent, Runner as OARunner, set_default_openai_client
    from agents.agent_output import AgentOutputSchemaBase
    from agents.exceptions import ModelBehaviorError
    from agents import function_tool

except Exception as e:
    raise ImportError(
        "The OpenAI Agents SDK is required for the 'openai-agents' provider. "
        "Install with: pip install openai-agents"
    ) from e

try:
    from openai import AsyncOpenAI, AsyncAzureOpenAI
except Exception as e:
    raise ImportError(
        "The openai package is required."
        "Install with: pip install openai"
    ) from e

# Optional MCP classes (pip install openai-agents) – enabled if present
try:
    from agents.mcp import MCPServerSse, MCPServerStreamableHttp, MCPServer  # type: ignore
    _HAS_MCP = True
except Exception:
    MCPServerSse = MCPServerStreamableHttp = MCPServer = None  # type: ignore
    _HAS_MCP = False

# Optional OpenAI upload client (only needed for local file uploads in UserMessageBuilder)
try:
    from openai import OpenAI
    _HAS_OPENAI = True
except Exception:
    OpenAI = None  # type: ignore
    _HAS_OPENAI = False

# Optional JSON Schema validation
try:
    from jsonschema import Draft202012Validator
    _HAS_JSONSCHEMA = True
except ImportError:
    Draft202012Validator = None  # type: ignore
    _HAS_JSONSCHEMA = False


class JsonSchemaOutput(AgentOutputSchemaBase):
    """
    Wrapper that passes a JSON schema to the Agents SDK.
    - If `jsonschema` is available: validate against Draft2020-12.
    - If not: fallback to plain `json.loads` without schema validation.
    """

    def __init__(self, name: str, schema: Dict[str, Any], strict: bool = True):
        self._name = name
        self._schema = schema
        self._strict = strict
        self._validator = Draft202012Validator(schema) if _HAS_JSONSCHEMA else None

    # --- required methods ---
    def is_plain_text(self) -> bool:
        return False  # expecting structured JSON, not plain text

    def name(self) -> str:
        return self._name

    def json_schema(self) -> Dict[str, Any]:
        return self._schema

    def is_strict_json_schema(self) -> bool:
        return self._strict

    def validate_json(self, json_str: str) -> Any:
        try:
            obj = json.loads(json_str)
        except Exception as e:
            raise ModelBehaviorError(f"Model did not return valid JSON: {e}")

        if self._validator:
            errors = list(self._validator.iter_errors(obj))
            if errors:
                err = errors[0]
                raise ModelBehaviorError(
                    f"JSON did not match schema at "
                    f"{list(err.absolute_path)}: {err.message}"
                )
        return obj







import ast

def _compile_top_level_function(code_str: str):
    """
    Compile `code_str` and return (callable, discovered_name) for the FIRST top-level def.
    Raises if none found or not callable.
    """
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


def _toolspecs_to_decorated_tools(toolspecs: List[Dict[str, Any]]):
    """
    Convert [{'code': <str>, 'attributes': {'id': <name>?}}, ...] into a list
    of function_tool-wrapped callables understood by the Agents SDK.

    - If attributes.id exists, it becomes the tool name by renaming fn.__name__.
    - The function's docstring is used as the tool description.
    """
    tools_out = []
    for i, spec in enumerate(toolspecs):
        if not isinstance(spec, dict) or "code" not in spec:
            raise TypeError(f"Tool #{i} must be a dict with a 'code' key.")
        fn, _discovered = _compile_top_level_function(spec["code"])
        attrs = (spec.get("attributes") or {})
        tool_name = attrs.get("id")

        if tool_name:
            # function_tool uses the Python function name; rename before wrapping
            try:
                fn.__name__ = tool_name
            except Exception:
                # Some callables may not allow __name__ set; fall back to wrapper
                def _alias(*args, __fn=fn, **kwargs):
                    return __fn(*args, **kwargs)
                _alias.__name__ = tool_name
                _alias.__doc__ = getattr(fn, "__doc__", None)
                fn = _alias

        wrapped = function_tool(fn)  # no kwargs supported in this SDK version
        tools_out.append(wrapped)
    return tools_out


def _normalize_tools(tools_in: Any):
    """
    Accepts multiple shapes and returns a list of tools suitable for OAAgent:
      - Your shape: [{'code': str, 'attributes': {...}}, ...]
      - Already-wrapped tools (have .name) -> pass through
      - A single callable -> decorate with function_tool
      - List of callables -> decorate each
      - Mapping {name: callable} -> rename and decorate each
    """
    if tools_in is None:
        return None

    # Your shape
    if isinstance(tools_in, list) and tools_in and isinstance(tools_in[0], dict) and "code" in tools_in[0]:
        return _toolspecs_to_decorated_tools(tools_in)

    # Already-wrapped tools (FunctionTool-ish objects typically expose .name)
    if hasattr(tools_in, "name"):
        return [tools_in]

    # Mapping name -> callable
    if isinstance(tools_in, dict) and tools_in and all(callable(v) for v in tools_in.values()):
        out = []
        for name, fn in tools_in.items():
            try:
                fn.__name__ = name
            except Exception:
                def _alias(*args, __fn=fn, **kwargs):
                    return __fn(*args, **kwargs)
                _alias.__name__ = name
                _alias.__doc__ = getattr(fn, "__doc__", None)
                fn = _alias
            out.append(function_tool(fn))
        return out

    # List of items
    if isinstance(tools_in, list):
        out = []
        for t in tools_in:
            if hasattr(t, "name"):
                out.append(t)  # already a tool object
            elif callable(t):
                out.append(function_tool(t))
            elif isinstance(t, dict) and "code" in t:
                # handle mixed list that includes your spec(s)
                out.extend(_toolspecs_to_decorated_tools([t]))
            else:
                raise TypeError(
                    f"Unsupported tool entry: {t!r}. "
                    "Provide function_tool-wrapped tools, callables, your {'code','attributes'} shape, "
                    "or a {name: callable} mapping."
                )
        return out

    # Single callable
    if callable(tools_in):
        return [function_tool(tools_in)]

    raise TypeError(
        f"Unsupported tools type: {type(tools_in)}. "
        "Provide function_tool-wrapped tools, callables, your [{'code','attributes'}] shape, "
        "or a {name: callable} mapping."
    )

class OpenAIAgentsAdapter(ProviderAdapter):
    def __init__(self, config: Dict[str, Any]):
        self.config = dict(config or {})

    @classmethod
    def is_valid_config(cls, config: Optional[Dict[str, Any]] = None) -> bool:
        cfg = config or {}
        return True

    async def run(
        self,
        input_text: str,
        *,
        message_history: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = "",
        tools: Optional[Any] = None,
        output_type: Optional[OutputType] = None,
        mcp_servers: Optional[List[Dict[str, Any]]] = None,
        links: Optional[List[Dict[str, Any]]] = None,
        images: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> RunResponse:
        
        # ---- Fast path: final answer provided --------------------------------
        custom_output_text = kwargs.pop("custom_output_text", None)
        if custom_output_text is not None:
            mh = message_history or []
            filtered_hist = [m for m in mh if isinstance(m, dict) and m.get("role") != "system"]
            all_messages: List[Dict[str, Any]] = []
            all_messages.extend(filtered_hist)
            all_messages.append({"role": "user", "content": input_text})
            all_messages.append({"role": "assistant", "content": custom_output_text})
            return RunResponse(output=custom_output_text, all_messages=all_messages)
            
        client = resolve_client( self.config )
        if client is None:
            raise RuntimeError("No valid configuration for OpenAI or Azure found!")

        set_default_openai_client( client )

        # ---- Build Agent (handle model fallback) -----------------------------
        agent_name = self.config.get("name", "Assistant")
        instructions = (system_prompt or self.config.get("system_prompt") or "").strip()

        # pull possibly-problematic kwargs so they don't leak into Runner.run
        model_hint = self.config.get("model", None) 
        client = kwargs.pop("client", None)

        agent_kwargs: Dict[str, Any] = {"name": agent_name}
        if instructions:
            agent_kwargs["instructions"] = instructions

        if tools is not None:
            agent_kwargs["tools"] = _normalize_tools(tools)

        # reflect Agent ctor
        agent_init_params = set(inspect.signature(OAAgent).parameters.keys())
        if client is not None and "client" in agent_init_params:
            agent_kwargs["client"] = client

        if model_hint is not None:
            if "model" in agent_init_params:
                agent_kwargs["model"] = model_hint
            else:
                # Fallback: annotate the instructions so the hint is preserved
                hint = f"(model: {model_hint})"
                agent_kwargs["instructions"] = (
                    f"{agent_kwargs.get('instructions','')}\n{hint}".strip()
                )

        # Output type wiring
        if isinstance(output_type, dict):
            agent_kwargs["output_type"] = JsonSchemaOutput("Schema", output_type, strict=True)
        elif output_type is not None:
            try:
                from pydantic import BaseModel as PydBaseModel
            except ImportError:
                raise ImportError(
                    "Pydantic is not installed. Please install it with 'pip install pydantic' "
                    "if you want to use a BaseModel as output_type."
                )
            if (
                isinstance(output_type, PydBaseModel)
                or (isinstance(output_type, type) and issubclass(output_type, PydBaseModel))
            ):
                agent_kwargs["output_type"] = output_type
            else:
                raise TypeError(
                    f"Invalid type for output_type: {type(output_type)}. "
                    "Allowed values are dict (JSON Schema) or a Pydantic BaseModel."
                )

        # ---- Build the MCP servers (pattern: create instances, use async context) ----
        server_instances: List[Any] = []
        if mcp_servers:
            if not _HAS_MCP:
                warnings.warn(
                    "agents.mcp is not available; ignoring provided mcp_servers.",
                    RuntimeWarning,
                )
            else:
                for idx, entry in enumerate(mcp_servers):
                    if not isinstance(entry, dict):
                        warnings.warn(f"Ignoring MCP entry #{idx}: not a dict ({type(entry)})")
                        continue

                    url = (entry.get("href") or entry.get("url") or "").strip()
                    if not url:
                        warnings.warn(f"Ignoring MCP entry #{idx}: missing 'url'/'href'")
                        continue

                    headers = entry.get("headers") or {}
                    name = entry.get("name") or f"MCP Server {idx+1}"
                    cache_tools_list = entry.get("cache_tools_list", True)

                    # Decide transport by URL suffix (your server uses /mcp)
                    try:
                        if url.endswith("/sse") and MCPServerSse is not None:
                            server_instances.append(MCPServerSse(
                                name=name,
                                params={"url": url, "headers": headers},
                                cache_tools_list=cache_tools_list,
                            ))
                        elif url.endswith("/mcp") and MCPServerStreamableHttp is not None:
                            server_instances.append(MCPServerStreamableHttp(
                                name=name,
                                params={"url": url, "headers": headers},
                                cache_tools_list=cache_tools_list,
                            ))
                        else:
                            warnings.warn(
                                f"Unrecognized MCP URL (must end with /sse or /mcp): {url}",
                                RuntimeWarning,
                            )
                    except Exception as e:
                        warnings.warn(f"Failed to configure MCP server for url={url!r}: {e}", RuntimeWarning)

        # ---- Build multimodal user message -----------------------------------
        builder = UserMessageBuilder(prefer_upload=True)
        msg = builder.build(
            user_text=input_text,
            images=[i.get("src") for i in images] if images else [],
            links=[l.get("href") for l in links] if links else [],
        )

        # ---- Prepare input ---------------------------------------------------
        mh = message_history or []
        if not isinstance(mh, list):
            raise TypeError("message_history must be a list of messages or None")
        filtered_hist = [m for m in mh if isinstance(m, dict) and m.get("role") != "system"]
        turn_input: Union[str, List[Dict[str, Any]]] = filtered_hist + [msg]

        # keep only kwargs supported by Runner.run to avoid surprises
        runner_params = set(inspect.signature(OARunner.run).parameters.keys())
        run_kwargs = {k: v for k, v in kwargs.items() if k in runner_params}

        # ---- Enter MCP contexts (if any), then build Agent, then run ---------
        async with AsyncExitStack() as stack:
            # enter each MCP server's async context (matches your pattern)
            entered_servers: List[Any] = []
            for srv in server_instances:
                try:
                    entered = await stack.enter_async_context(srv)
                    entered_servers.append(entered)
                except Exception as e:
                    warnings.warn(f"Failed to enter MCP server context: {e}", RuntimeWarning)

            if entered_servers:
                agent_kwargs["mcp_servers"] = entered_servers

                # Optional: force tool usage if you want the model to actually call MCP tools
                # If you prefer to control via config, set model_settings in self.config.
                try:
                    from agents.model_settings import ModelSettings
                    ms = self.config.get("model_settings")
                    if isinstance(ms, dict):
                        agent_kwargs["model_settings"] = ModelSettings(**ms)
                    elif self.config.get("tool_choice_required", False):
                        agent_kwargs["model_settings"] = ModelSettings(tool_choice="required")
                except Exception as e:
                    warnings.warn(
                        f"Failed to apply model_settings: {e}. "
                        "Proceeding without default ModelSettings.",
                        RuntimeWarning,
                    )

            agent = OAAgent(**agent_kwargs)

            # ---- Execute ---------------------------------------------------------
            result = await OARunner.run(agent, turn_input, **run_kwargs)

        # ---- Extract output & rebuild messages ----------------------------------
        output = getattr(result, "final_output", None)
        if output is None:
            output = getattr(result, "output", None)
        if output is None:
            output = getattr(result, "text", None)
        if output is None:
            output = str(result)

        all_messages: List[Dict[str, Any]] = []
        all_messages.extend(filtered_hist)
        all_messages.append({"role": "user", "content": input_text})
        all_messages.append({"role": "assistant", "content": output})

        return RunResponse(output=output, all_messages=all_messages)


class UserMessageBuilder:
    def __init__(self, prefer_upload: bool = True):
        """
        :param prefer_upload: True = try uploading local files (requires openai package).
                              False = always fallback to data:-URL.
        """
        self.prefer_upload = prefer_upload

    # ---------- internal helpers ----------
    def _file_to_data_url(self, path: str) -> str:
        """Convert a local file into a one-line data:-URL (Base64)."""
        mime, _ = mimetypes.guess_type(path)
        if not mime:
            mime = "application/octet-stream"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    def _resolve_image(self, image_source: str) -> str:
        """Return a valid image_url string (http/https OR data:-URL for local)."""
        if image_source.startswith(("http://", "https://")):
            return image_source
        if not os.path.isfile(image_source):
            raise FileNotFoundError(f"Image not found: {image_source}")
        return self._file_to_data_url(image_source)

    def _resolve_file(self, file_source: str) -> Tuple[str, str]:
        """
        Return (mode, value) for input_file:
          - ("file_url", "<http/https-url>") for remote files
          - ("file_id", "<file_...>") if local and uploaded
          - ("file_url", "<data:-URL>") fallback if upload not available
        """
        if file_source.startswith(("http://", "https://")):
            return ("file_url", file_source)

        if not os.path.isfile(file_source):
            raise FileNotFoundError(f"File not found: {file_source}")

        if self.prefer_upload and _HAS_OPENAI:
            try:
                client = OpenAI()
                with open(file_source, "rb") as f:
                    uploaded = client.files.create(file=f, purpose="assistants")
                return ("file_id", uploaded.id)
            except Exception as e:
                print(f"[warn] Upload failed for {file_source}, using data:-URL fallback. Reason: {e}")

        return ("file_url", self._file_to_data_url(file_source))

    # ---------- public ----------
    def build(
        self,
        user_text: str,
        images: Optional[List[str]] = None,
        links: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Build a full user message for the Agents Runner.

        :param user_text: The main text query from the user.
        :param images: A list of image paths or URLs.
        :param links: A list of file paths (PDF/docs) or URLs.
        :return: {"role": "user", "content": [...]}
        """
        content: List[Dict[str, Any]] = []

        if user_text:
            content.append({"type": "input_text", "text": user_text})

        for img in images or []:
            url = self._resolve_image(img)
            content.append({"type": "input_image", "image_url": url})

        for link in links or []:
            mode, value = self._resolve_file(link)
            content.append({"type": "input_file", mode: value})

        return {"role": "user", "content": content}

def resolve_client(cfg: Dict[str, Any]) -> Optional[object]:
    """
    Takes a dict (cfg) as input and checks whether it is complete for OpenAI or Azure.
    If yes: returns a matching AsyncOpenAI or AsyncAzureOpenAI client.
    If not: tries environment variables.
    If nothing matches: returns None.
    """

    # ---- Definition der beiden Varianten ----
    required_openai = ["api_key"]  # base_url optional
    required_azure = ["api_key", "api_version", "azure_endpoint", "azure_deployment"]

    def is_complete(d: Dict[str, Any], required: list[str]) -> bool:
        return all(d.get(k) for k in required)

    # 1) Direkt prüfen, ob cfg vollständig ist
    if is_complete(cfg, required_openai):
        return AsyncOpenAI(
            api_key=cfg["api_key"],
            base_url=cfg.get("base_url", "https://api.openai.com/v1")
        )

    if is_complete(cfg, required_azure):
        return AsyncAzureOpenAI(
            api_key=cfg["api_key"],
            api_version=cfg["api_version"],
            azure_endpoint=cfg["azure_endpoint"],
            azure_deployment=cfg["azure_deployment"]
        )

    # 2) Umgebungsvariablen prüfen
    env_openai = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    }
    if is_complete(env_openai, required_openai):
        return AsyncOpenAI(**env_openai)

    env_azure = {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
        "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "azure_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    }
    if is_complete(env_azure, required_azure):
        return AsyncAzureOpenAI(**env_azure)

    # 3) Nichts gefunden
    return None

def factory(config: Optional[Dict[str, Any]] = None) -> OpenAIAgentsAdapter:
    return OpenAIAgentsAdapter(config or {})
