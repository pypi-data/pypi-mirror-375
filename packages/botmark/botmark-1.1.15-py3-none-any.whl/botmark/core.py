# core.py
from __future__ import annotations

import asyncio, copy, inspect, json, os, traceback, uuid
from typing import Any, Optional, Union, TextIO, Dict
import logging

logger = logging.getLogger(__name__)

# ----------------------------
# Optional .env loading
# ----------------------------
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args, **_kwargs):
        logger.warning("⚠️  python-dotenv is not installed; environment files (.env) will be ignored.")
        return None

load_dotenv()

# ----------------------------
# Local imports (your project)
# ----------------------------
from .config import Settings
from .markdown_parser.parser import parse_to_json
from .responder import engine
from .sources import FileSystemSource, BotmarkSource, StringSource
from .runners import create_ai_runner, Runner
from .utils.helpers import (
    apply_modifiers,
    traverse_graph,
    parse_markdown_to_qa_pairs,
    get_graph,
    interpret_bool_expression,
    get_tools,
    find_active_topics,
    get_blocks,
    get_header,
    get_images,
    process_links,
    get_schema,
    render_block,
    render_named_block,
    try_answer,
    make_answer,
)
from . import __version__ as VERSION

# Telemetry DI
from .telemetry import TelemetrySink, NoOpTelemetrySink, StepTimer, create_telemetry

class BotMarkAgent:
    def __init__(self, botmark_json: dict, runner: Runner, telemetry: TelemetrySink | None = None):
        self.botmark_json = botmark_json
        self.runner = runner
        self.telemetry: TelemetrySink = telemetry or NoOpTelemetrySink()

    def __eq__(self, other):
        if isinstance(other, BotMarkAgent):
            return self.botmark_json == other.botmark_json
        return False

    def __hash__(self):
        return hash(frozenset(self.botmark_json.items()))

    def clone(self, include_graphs: bool = True):
        botmark_json = copy.deepcopy(self.botmark_json)
        if not include_graphs:
            botmark_json["graphs"] = []
        # keep same runner & telemetry for clones (e.g., graph sub-agents)
        return BotMarkAgent(botmark_json=botmark_json, runner=self.runner, telemetry=self.telemetry)

    def get_framework_info(self) -> str:
        """Returns pretty JSON string with runner/framework info."""
        try:
            info = self.runner.get_info() if hasattr(self.runner, "get_info") else {}
            return json.dumps(info, indent=4, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=4, ensure_ascii=False)

    def get_info(self):
        return self.botmark_json.get("info", "<p>info not found</p>")

    def get_tests(self):
        test_cases = []
        ranking_function = lambda block: 1 if "unittest" in block.get("classes", []) else -1
        unittests = get_blocks(self.botmark_json["codeblocks"], ranking_function=ranking_function)

        for test_name, test_block in unittests.items():
            qa_list = parse_markdown_to_qa_pairs(test_block.get("content"))
            if not qa_list:
                continue
            test_cases.append((test_name, qa_list))

        return test_cases

    def validate(self):
        pass

    async def run(self, user_input, **kwargs) -> Any:
        """
        Main agent entrypoint. Structured telemetry is emitted for each major step.
        """
        run_id = kwargs.pop("run_id", None) or str(uuid.uuid4())

        # Normalize user_text early so we can reference it in telemetry
        if isinstance(user_input, str):
            user_text = user_input
        elif isinstance(user_input, list):
            user_text = "".join([s for s in user_input if isinstance(s, str)])
        else:
            user_text = str(user_input)

        logger.debug("telemetry sink = %s", type(self.telemetry).__name__)
        await self.telemetry.start(run_id, {
            "version": VERSION,
            "runner_info": (self.runner.get_info() if hasattr(self.runner, "get_info") else {}),
            "kwargs_keys": list(kwargs.keys()),
        })

        try:
            tables = self.botmark_json.get("tables", {})
            topics_table = tables.get("topic")

            # ----------------------------
            # Resolve topics
            # ----------------------------
            async with StepTimer(self.telemetry, run_id, "resolve_topics", {"has_topic_table": bool(topics_table)}):
                topics: Dict[str, Any] = {}
                if topics_table:
                    topics = find_active_topics(topics_table, user_text)
                await self.telemetry.step(run_id, "topics", {"topics": topics})

            # ----------------------------
            # Select & modify active blocks
            # ----------------------------
            def ranking_fn(block):
                return interpret_bool_expression(block.get("attributes", {}).get("match"), topics)

            async with StepTimer(self.telemetry, run_id, "select_blocks"):
                active_blocks = get_blocks(self.botmark_json["codeblocks"], ranking_fn)
                initial_history = kwargs.get("message_history", [])
                active_blocks = apply_modifiers(active_blocks, user_text, initial_history)
                await self.telemetry.step(run_id, "blocks.selected", {
                    "count": len(active_blocks),
                    "keys": list(active_blocks.keys())
                })

            # ----------------------------
            # Compose context (graph/header/images/links)
            # ----------------------------
            async with StepTimer(self.telemetry, run_id, "compose_context"):
                active_graph = get_graph(self.botmark_json["graphs"], ranking_fn)
                active_header = get_header(active_blocks, self.botmark_json["header"])

                predicate = lambda block: interpret_bool_expression(block.get("match"), topics) >= 0
                active_images = get_images(self.botmark_json.get("images", []), predicate)
                active_links, mcp_servers = process_links(self.botmark_json.get("links", []), predicate)

                query_images: list[dict] = []
                query_links: list[dict] = []
                if active_header.get("inspect_user_prompt", False):
                    query_objects = parse_to_json(user_text) if active_header.get("inspect_user_prompt", False) is True else {}
                    query_images = get_images(query_objects.get("images", []), lambda x: True)
                    query_links, _ = process_links(query_objects.get("links", []), lambda x: True)

                images = active_images + query_images
                links = active_links + query_links

                await self.telemetry.step(run_id, "context.composed", {
                    "has_graph": bool(active_graph),
                    "images_count": len(images),
                    "links_count": len(links),
                    "mcp_count": len(mcp_servers or []),
                })

            answer = None

            # ----------------------------
            # Graph path (if present)
            # ----------------------------
            if active_graph:
                async with StepTimer(self.telemetry, run_id, "graph.traverse", {
                    "nodes": list(active_graph["graph"]["nodes"].keys())
                }):
                    def filter_funktion(_key, value):
                        return "agent" in value.get("classes", [])

                    active_agents = {k: v for k, v in active_blocks.items() if filter_funktion(k, v)}
                    processors: Dict[str, BotMarkAgent] = {"[*]": self.clone(include_graphs=False)}

                    for node in active_graph["graph"]["nodes"].keys():
                        if node in active_agents.keys():
                            bot_json = active_agents[node].get("content", {})
                            processors[node] = BotMarkAgent(botmark_json=bot_json, runner=self.runner, telemetry=self.telemetry)
                        elif node not in processors:
                            # fail fast: agent missing
                            raise ValueError(
                                f"Graph node '{node}' has no matching agent definition "
                                f"in active_blocks. Define an agent for this node."
                            )

                    histories, transcript, answer = await traverse_graph(
                        graph_obj=active_graph,
                        processors=processors,
                        initial_history=initial_history,
                        runner=self.runner,
                        start_message=user_text
                    )
                    await self.telemetry.step(run_id, "graph.result", {
                        "has_answer": bool(answer),
                        "transcript_len": len(transcript or []),
                        "histories_len": len(histories or []),
                    })

            # ----------------------------
            # Fallback path (no graph or no graph answer)
            # ----------------------------
            if not answer:
                async with StepTimer(self.telemetry, run_id, "prompt_and_schema"):
                    active_schema = get_schema(active_blocks, topics)

                    VENV_BASE_DIR = active_header.get("VENV_BASE_DIR", Settings.VENV_BASE_DIR)
                    active_prompt = active_blocks.get("prompt")
                    final_query = render_block(active_prompt, {"QUERY": user_text}) if active_prompt else user_text

                    active_system = render_named_block(
                        "system",
                        active_blocks,
                        active_header,
                        VERSION,
                        final_query,
                        topics,
                        images,
                        links,
                        mcp_servers,
                        VENV_BASE_DIR,
                        {},
                    )

                    await self.telemetry.step(run_id, "prompt.prepared", {
                        "has_schema": bool(active_schema),
                        "system_len": len(active_system or ""),
                        "final_query_preview": (final_query or "")[:200],
                    })

                # Try to answer locally (synchronous heuristics)
                local_answer = try_answer(
                    active_blocks,
                    active_system,
                    active_header,
                    VERSION,
                    final_query,
                    VENV_BASE_DIR,
                    topics,
                    images,
                    links,
                    mcp_servers,
                )

                if local_answer is not None:
                    answer = local_answer
                else:
                    # Call runner/LLM
                    async with StepTimer(self.telemetry, run_id, "runner.call", {
                        "tools_count": len(get_tools(active_blocks) or []),
                        "images_count": len(images),
                        "links_count": len(links),
                    }):
                        active_tools = get_tools(active_blocks)
                        composed_input = final_query

                        result = await self.runner(
                            composed_input,
                            system_prompt=active_system,
                            tools=active_tools,
                            images=images,
                            links=links,
                            mcp_servers=mcp_servers,
                            output_type=active_schema,
                            **kwargs
                        )

                        out = result.output
                        if hasattr(out, "model_dump_json") and callable(out.model_dump_json):
                            llm_response = out.model_dump_json()
                        elif isinstance(out, (dict, list)):
                            llm_response = json.dumps(out, ensure_ascii=False)
                        elif out is None:
                            raise ValueError("Agent returned no output (None).")
                        else:
                            llm_response = str(out)

                        await self.telemetry.step(run_id, "runner.output", {
                            "output_preview": (llm_response or "")[:500],
                        })

                    async with StepTimer(self.telemetry, run_id, "make_answer"):
                        answer = make_answer(
                            active_blocks,
                            active_system,
                            active_header,
                            VERSION,
                            final_query,
                            llm_response,
                            VENV_BASE_DIR,
                            topics,
                            images,
                            links,
                            mcp_servers,
                        )
                        await self.telemetry.step(run_id, "answer.composed", {"answer_len": len(answer or "")})

            # ----------------------------
            # Finalize: echo custom_output to collect transcript
            # ----------------------------
            async with StepTimer(self.telemetry, run_id, "finalize"):
                result = await self.runner(
                    user_input,
                    custom_output_text=answer,
                    **kwargs
                )
                await self.telemetry.end(run_id, {"ok": True})
                return result

        except Exception as e:
            tb = traceback.format_exc()
            await self.telemetry.error(run_id, {"message": str(e), "traceback": tb})
            await self.telemetry.end(run_id, {"ok": False})
            return await self.runner(
                user_input,
                custom_output_text=f'ERROR: {str(e)}',
                **kwargs
            )

    def run_sync(self, *args, **kwargs) -> Any:
        """
        Synchronously execute the async `run` method.
        Works when no event loop is running and, if already inside a loop (e.g. Jupyter),
        tries nest_asyncio; otherwise tells the caller to await.
        """
        target = self.run(*args, **kwargs)

        # In case run was (accidentally) made sync:
        if not inspect.isawaitable(target):
            return target

        try:
            return asyncio.run(target)
        except RuntimeError as e:
            # Typically: "asyncio.run() cannot be called from a running event loop"
            if "running event loop" not in str(e):
                raise

        # Already inside a running loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop after all; create one
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(target)
            finally:
                loop.close()

        # A loop is running; try nest_asyncio to allow nesting
        try:
            import nest_asyncio  # type: ignore
            nest_asyncio.apply()
            return loop.run_until_complete(target)
        except Exception as inner:
            raise RuntimeError(
                "run_sync was called inside a running event loop. "
                "Please use 'await self.run(...)' instead."
            ) from inner


class BotManager:
    def __init__(
        self,
        default_model: Optional[Union[str, dict, TextIO]] = None,
        adapt_payload=lambda x: x,
        response_parser=lambda x: x.output,
        allow_code_execution: bool = False,
        botmark_source=None,
        default_runner: Runner = create_ai_runner("pydantic-ai", {}),
        default_telemetry: TelemetrySink | None = None,
    ):
        if botmark_source is None:
            botmark_source = [FileSystemSource(".")]
        elif not isinstance(botmark_source, list):
            botmark_source = [botmark_source]

        self.botmark_sources = botmark_source
        self.adapt_payload = adapt_payload
        self.response_parser = response_parser
        self.allow_code_execution = allow_code_execution
        self.botmark_source = botmark_source
        self.default_runner = default_runner
        self.default_telemetry = default_telemetry or NoOpTelemetrySink()

        self.agent: Optional[BotMarkAgent] = None
        if hasattr(default_model, "read"):
            self.agent = self.get_agent(default_model.read())
        elif isinstance(default_model, str):
            self.agent = self._get_agent_from_model_name(default_model)
        elif isinstance(default_model, dict):
            self.agent = self.get_agent(default_model)

    def get_framework_info(self, model_name: Optional[str] = None):
        model_data = self._load_from_sources(model_name)
        if model_data:
            return self.get_agent(parse_to_json(model_data)).get_framework_info()
        return self.agent.get_framework_info() if self.agent else "{}"

    def get_info(self, model_name: Optional[str] = None):
        model_data = self._load_from_sources(model_name)
        if model_data:
            return self.get_agent(parse_to_json(model_data)).get_info()
        return self.agent.get_info() if self.agent else "<p>info not found</p>"

    def get_agent(self, bot_definition: Union[str, dict]):
        bot_json = bot_definition if isinstance(bot_definition, dict) else parse_to_json(bot_definition)

        if not self.allow_code_execution:
            disallowed = {"mako", "python", "fstring"}
            kept = []

            for i, block in enumerate(bot_json.get("codeblocks", []) or []):
                lang = (block.get("language") or "").lower()
                if lang in disallowed:
                    ident = (
                        block.get("id")
                        or block.get("name")
                        or (block.get("attributes") or {}).get("id")
                        or (block.get("attributes") or {}).get("name")
                        or f"index:{i}"
                    )
                    print(f"⚠️ allow_code_execution=False — filtered codeblock '{ident}' (language='{lang}')")
                else:
                    kept.append(block)

            bot_json["codeblocks"] = kept

        agent_kwargs: Dict[str, Any] = {
            "botmark_json": bot_json,
        }

        # ---------------------------
        # Runner selection
        # ---------------------------
        header = bot_json.get("header", {}) or {}
        framework_data = header.get("framework", None)
        if framework_data:
            agent_kwargs["runner"] = create_ai_runner(framework_data.get("name", ""), framework_data.get("config", {}))
        elif Settings.FRAMEWORK_NAME and Settings.FRAMEWORK_CONFIG:
            agent_kwargs["runner"] = create_ai_runner(Settings.FRAMEWORK_NAME, Settings.FRAMEWORK_CONFIG)
        elif Settings.FRAMEWORK_NAME:
            agent_kwargs["runner"] = create_ai_runner(Settings.FRAMEWORK_NAME, {})
        else:
            agent_kwargs["runner"] = self.default_runner

        telemetry = header.get("telemetry")
        if telemetry:
            agent_kwargs["telemetry"] = create_telemetry(telemetry)
        elif Settings.TELEMETRY:
            agent_kwargs["telemetry"] = create_telemetry(Settings.TELEMETRY)
        else:
            agent_kwargs["telemetry"] = self.default_telemetry

        agent = BotMarkAgent(**agent_kwargs)
        return agent

    def _get_agent_from_model_name(self, model_name):
        model_data = parse_to_json(self._load_from_sources(model_name))
        return self.get_agent(model_data) if model_data else None

    def get_tests(self):
        tests = [{"model": "", "tests": self.agent.get_tests()}] if self.agent else []
        for model_info in self.get_models().get("data", []):
            model_id = model_info["id"]
            bm_code = parse_to_json(self._load_from_sources(model_id))
            agent = self.get_agent(bm_code)
            tests += [{"model": model_id, "tests": agent.get_tests()}]
        return tests

    def get_models(self) -> dict:
        all_models = {"object": "list", "data": []}
        seen_ids = set()
        for source in self.botmark_sources:
            models = source.list_models().get("data", [])
            for m in models:
                if m["id"] not in seen_ids:
                    all_models["data"].append(m)
                    seen_ids.add(m["id"])
        return all_models

    def _load_from_sources(self, model_id: str) -> Optional[str]:
        for source in self.botmark_sources:
            content = source.load_botmark(model_id)
            if content:
                return content
        return None

    def _model_exists(self, model_list: dict, model_id: str) -> bool:
        for model in model_list.get("data", []):
            if model.get("id") == model_id:
                return True
        return False

    def respond_sync(self, json_payload: dict) -> str:
        json_payload = self.adapt_payload(json_payload)
        model_name = json_payload.get("model", None)
        models = self.get_models()

        if self._model_exists(models, model_name):
            model_data = parse_to_json(self._load_from_sources(model_name))
            response = engine.respond(self.get_agent(model_data), json_payload)
        else:
            if self.agent:
                response = engine.respond(self.agent, json_payload)
            else:
                raise ValueError(
                    f"Model '{model_name}' not found, no fallback agent available, and system prompt fallback is disabled."
                )

        return self.response_parser(response)

    async def respond(self, json_payload: Dict) -> str:
        """
        Async counterpart to respond_sync: prepares payload, selects the agent,
        calls the engine asynchronously, and returns the parsed string response.
        """
        json_payload = self.adapt_payload(json_payload)
        model_name = json_payload.get("model", None)
        models = self.get_models()

        async def _call_engine_async(agent, payload):
            # Prefer a native async engine method; otherwise run sync in a thread.
            if hasattr(engine, "respond_async"):
                return await engine.respond_async(agent, payload)
            return await asyncio.to_thread(engine.respond, agent, payload)

        if self._model_exists(models, model_name):
            model_data = parse_to_json(self._load_from_sources(model_name))
            response = await _call_engine_async(self.get_agent(model_data), json_payload)
        else:
            if self.agent:
                response = await _call_engine_async(self.agent, json_payload)
            else:
                raise ValueError(
                    f"Model '{model_name}' not found, no fallback agent available, "
                    f"and system prompt fallback is disabled."
                )

        return self.response_parser(response)
