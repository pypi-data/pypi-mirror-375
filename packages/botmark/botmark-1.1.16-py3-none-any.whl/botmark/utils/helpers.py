from __future__ import annotations

import json, warnings
from enum import Enum
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Type, Mapping, Union, Set

# pydantic / pydantic-ai
#from pydantic import BaseModel, Field, create_model

import inspect

import re, json, time, os, sys, uuid, hashlib
import urllib.parse, importlib, textwrap, inspect, subprocess, base64
from .json_rag import apply_json_rag

import ast
import operator

#from openai.types.responses import WebSearchToolParam

from .yaml_parser import yaml
import importlib.util
import concurrent.futures

import logging
logger = logging.getLogger(__name__)

def apply_modifiers(blocks: dict, query: str, history ) -> dict:
    blocks = apply_json_rag( blocks, query, history )
    for key, block in blocks.items():
        limit_key = "max_items"
        if limit_key in block.attributes:
            try:
                limit = int(block.attributes[limit_key])
            except (ValueError, TypeError):
                continue  # skip if not an integer

            # only apply if content is a list
            if isinstance(block.content, list):
                if len(block.content) > limit:
                    logger.info(f"[apply_modifiers] limiting block '{key}' to {limit} items (was {len(block.content)})")
                    block.set("content", block.content[:limit])
        truncate_key = "truncate"
        if truncate_key in block.attributes:
            try:
                limit = int(block.attributes[truncate_key])
            except (ValueError, TypeError):
                continue  # skip if not an integer

            # only apply if content is a list
            if isinstance(block.content, str) and block.language in ["markdown", "text"]:
                if len(block.content) > limit:
                    logger.info(f"[apply_modifiers] limiting block '{key}' to {limit} characters (was {len(block.content)})")
                    block.set("content", block.content[:limit])

    return blocks

def get_header( blocks, default_header ):
    header_block = blocks.get("header", {})
    content = header_block.get("content", None)
    if header_block and isinstance(content, dict):
        return default_header | content
    return default_header

def find_active_topics(topics, user_input):
    status = {}
    matchers = {
        "prompt_prefix": lambda x: user_input.startswith ( x ),
        "prompt_suffix": lambda x: user_input.endswith ( x )  ,
        "prompt_regex": lambda x: re.search(x, user_input) is not None
        }

    for topic in topics:
        topic_name = topic['name']
        status[ topic_name ] = False
        for col_name in [ key for key in topic.keys() if key != "name"]:
            m = matchers.get( col_name )
            if callable( m ) and topic[col_name]:
                if m( topic[ col_name ] ):
                    status[topic_name] = True
    return status

ops = {
    ast.And: operator.and_,
    ast.Or: operator.or_,
    ast.Not: operator.not_,
}

def interpret_bool_expression(expr: str | None, context: dict) -> int:
    if expr is None:
        return 0

    ops = {
        ast.And: operator.and_,
        ast.Or: operator.or_,
    }

    used_vars = set()

    def _resolve(node):
        if isinstance(node, ast.BoolOp):
            values = [_resolve(v) for v in node.values]
            result = values[0]
            for v in values[1:]:
                result = ops[type(node.op)](result, v)
            return result
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return operator.not_(_resolve(node.operand))
        elif isinstance(node, ast.Name):
            used_vars.add(node.id)
            if node.id in context:
                return context[node.id]
            else:
                raise ValueError(f"Unknown variable: {node.id}")
        elif isinstance(node, ast.Expression):
            return _resolve(node.body)
        else:
            raise ValueError(f"Unsupported syntax in expression: {ast.dump(node)}")

    try:
        tree = ast.parse(expr.strip(), mode='eval')
        result = _resolve(tree)
        return len(used_vars) if result else -1
    except Exception:
        return -1

def find_topic(topics, user_input):

    # Check for trigger key match
    for item in topics:
        trigger_key = item.get('trigger key', None )
        if trigger_key and user_input.startswith(trigger_key):
            topic = item['name']
            stripped_input = user_input[len(trigger_key):].strip()
            return topic, stripped_input

    # Check for trigger regex match
    for item in topics:
        trigger_regex = item.get('trigger regex')
        if trigger_regex:
            match = re.match(trigger_regex, user_input)
            
            if match:
                topic = item['name']
                if match.lastindex:  # There is at least one capture group
                    return topic, match.group(1).strip()
                else:
                    return topic, match.group(0).strip()
    return None, user_input.strip()

class CodeBlock:
    def __init__(self, language=None, attributes=None, content="", classes=None):
        self.languages = [
            "json", "binary", "python", "xml", "html", "txt",
            "mako", "jinja2", "markdown", "md"
        ]

        attributes = attributes or {}
        classes = classes or []

        if language is None:
            language = next((name for name in self.languages if name in classes), None)
            if language:
                classes = [cls for cls in classes if cls != language]

        self.data = {
            "language": language,
            "attributes": attributes,
            "content": content,
            "classes": classes
        }

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        return self

    def __eq__(self, other):
        return isinstance(other, CodeBlock) and self.data == other.data

    def __hash__(self):
        return hash(json.dumps(self.data, sort_keys=True, ensure_ascii=False))

    def __repr__(self):
        return (
            f"CodeBlock("
            f"language={self.data['language']!r}, "
            f"attributes={self.data['attributes']!r}, "
            f"content={self.data['content']!r}, "
            f"classes={self.data['classes']!r})"
        )
    
    def __getattr__(self, name: str) -> Any:
        if name in self.data:
            return self.get(name)
        else:
            # warn about missing key
            warnings.warn(
                f"Key '{name}' not found. Available keys: {list(self.data.keys())}",
                stacklevel=2
            )
        return None

    # Optional, but handy: dictionary‑style indexing
    def __getitem__(self, key: str) -> Any:
        if key in self.data:        
            return self.get(key, None )
        else:
            # warn about missing key
            warnings.warn(
                f"Key '{key}' not found. Available keys: {list(self.data.keys())}",
                stacklevel=2
            )
        return None

    def to_json(self):
        return self.data

    @classmethod
    def from_json(cls, data):
        return cls(**data)

def get_images(images, predicate ):
    valid_images = []
    for image in images:
        if predicate ( image ):
            valid_images.append( image )
    return valid_images

def decode_data_url(data_url: str) -> tuple[str, bytes]:
    match = re.match(r'data:(.*?);base64,(.*)', data_url)
    if not match:
        raise ValueError("Ungültige Data-URL")
    media_type = match.group(1)
    data = base64.b64decode(match.group(2))
    return media_type, data

def process_links(links, predicate):
    valid_links = []
    mcp_servers = []

    for link in links:
        if predicate( link ):

            if "mcp" in link.get("class", []):
                mcp_servers.append( link )
            else:
                valid_links.append( link )
    return valid_links, mcp_servers

# get schema
def get_schema( blocks, TOPICS ):
    schema_block = blocks.get("schema", {})
    schema = schema_block.get("content", None)
    attrs = schema_block.get("attributes", {})
    name = attrs.get("root", "Schema")

    if schema:
        if schema_block.get("language") == "json":
            return schema_block.get("content")
        elif schema_block.get("language") == "python":
            new_classes = get_base_models(f"""
from typing import List
from pydantic import BaseModel, Field
TOPICS = {TOPICS}

{schema}
            """)

            named = new_classes.get(name, None)
            if named:
                return named
            return sorted(new_classes.items())[0] if new_classes else None
    return None

def get_base_models(code: str):
    try:
        # Compile first for clearer syntax errors
        compiled = compile(code, "<user_code>", "exec")

        # Isolated namespace for execution
        ns = {}

        # Execute user code
        exec(compiled, ns, ns)

        # Import after exec so our check is against the real pydantic BaseModel
        try:
            from pydantic import BaseModel
        except ImportError:
            raise SystemExit("❌ 'pydantic' is not installed. Please install with `pip install pydantic`.")

        # Gather all subclasses of BaseModel defined by the code
        classes = {
            name: obj
            for name, obj in ns.items()
            if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel
        }
        return classes

    except Exception as e:
        print(str(e))
        return {}

#### render named block
def get_block( name, blocks ):
    return blocks.get( name, None )

def create_directory( path ):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return True
    except Exception as e:
        return False

def hash_list(d):
    list_str = json.dumps(sorted( d ), ensure_ascii=False )
    return hashlib.blake2b(list_str.encode('utf-8'), digest_size=4).hexdigest()

def cleanup_tmp_folder(tmp_dir, max_files=10, min_age_seconds=86400):  # 1 day = 86400 seconds
    if not os.path.exists(tmp_dir):
        return  # No tmp folder, nothing to clean up

    # List only files with the correct prefix and extension
    files = [os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir)
             if os.path.isfile(os.path.join(tmp_dir, f)) and
             (f.startswith("template_") or f.startswith("data_")) and
             (f.endswith(".mako") or f.endswith(".json"))]

    if len(files) <= max_files:
        return  # No need to delete anything

    # Sort files by modification time (oldest first)
    files.sort(key=lambda f: os.stat(f).st_mtime)

    # Get the current timestamp
    current_time = time.time()

    # Select files to delete (only those older than min_age_seconds)
    files_to_delete = [f for f in files if (current_time - os.stat(f).st_mtime) > min_age_seconds]

    # Delete the oldest files until only `max_files` remain
    for file in files_to_delete[:len(files) - max_files]:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

def parse_packages(package_string):
    return [p.strip() for p in package_string.split(",") if p.strip()] if isinstance( package_string, str) else []

def render_template_in_venv( template_str, data, packages=[], venv_base_dir= "/data/venvs"):

    # Ensure base directory for virtual environments exists
    create_directory(venv_base_dir)

    # Generate a unique environment name based on the template content
    env_name = os.path.join(venv_base_dir, hash_list(packages))

    # Ensure virtual environment directory exists
    create_directory(env_name)

    # Create a dedicated tmp folder inside the virtual environment
    tmp_dir = os.path.join(env_name, "tmp")
    create_directory(tmp_dir)

    # Generate unique filenames for temporary files
    unique_id = str(uuid.uuid4())
    temp_template_path = os.path.join(tmp_dir, f"template_{unique_id}.mako")
    temp_data_path = os.path.join(tmp_dir, f"data_{unique_id}.json")

    # Write template and data to temporary files
    with open(temp_template_path, "w", encoding="utf-8") as temp_template:
        # write the template_str as base 64 encoded  !!
        temp_template.write(template_str)

    with open(temp_data_path, "w", encoding="utf-8") as temp_data:
        json.dump(data, temp_data)

    # Python script to execute within the virtual environment
    script_content_template = textwrap.dedent(f"""
        import json
        from mako.template import Template

        def render_template(template_str, data):
            template = Template(template_str)
            return template.render(**data)

        with open({json.dumps(temp_template_path, ensure_ascii=False)}, 'r') as f:
            template_str = f.read() # decode the base 64 string here!!

        with open({json.dumps(temp_data_path, ensure_ascii=False)}, 'r') as f:
            data = json.load(f)

        print(render_template(template_str, data))
        """)

    # Step 1: Create virtual environment if it does not exist
    if not os.path.exists(os.path.join(env_name, "bin" if os.name != "nt" else "Scripts")):
        try:
            subprocess.check_call([sys.executable, "-m", "venv", env_name])

            # Get the pip executable path
            pip_path = os.path.join(env_name, "Scripts" if os.name == "nt" else "bin", "pip")

            # Ensure Mako is always installed
            package_list = ["mako"] + [f"{package}" for package in packages]

            # Install all required packages
            subprocess.check_call([pip_path, "install"] + package_list)

        except subprocess.CalledProcessError as e:
            return f"Error setting up virtual environment: {e}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"

    # Step 2: Run the script in the virtual environment
    try:
        python_path = os.path.join(env_name, "Scripts" if os.name == "nt" else "bin", "python")
        result = subprocess.check_output([python_path, "-c", script_content_template], text=True)
        result = result[:-1] if result.endswith("\n") else result
    except subprocess.CalledProcessError as e:
        result = f"Error during script execution: {e}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"

    # Step 3: Clean up temporary files
    os.remove(temp_template_path)
    os.remove(temp_data_path)

    # Perform cleanup of old temp files
    cleanup_tmp_folder(tmp_dir)

    return result

def render_fstring(template: str, context: dict) -> str:
    # NOTE: This uses eval to get full f-string power. Only safe if templates are trusted.
    f_template = f"f'''{template}'''"
    return eval(f_template, {}, context)

def render_format(template: str, context: dict) -> str:
    return template.format(**context)

def render_block(block, data=None, venv_base_dir="/data/venvs"):
    create_directory(venv_base_dir)
    packages = parse_packages(block.get("attributes", {}).get("packages", ""))

    content = block.get("content", "")
    lang = (block.get("language", "") or "").lower()

    # normalize context
    context = data if isinstance(data, dict) else {"data": data}

    if "nostrip" in block.get("classes", []):
        strip_func = lambda x: x
    else:
        strip_func = lambda x: x.strip()

    try:
        if lang == "mako" and isinstance(data, dict):
            if len(packages) > 0:
                return strip_func( render_template_in_venv(content, data, packages=packages, venv_base_dir=venv_base_dir))
            else:
                try:
                    from mako.template import Template as MakoTemplate
                except ImportError:
                    return "⚠️  'mako' is not installed; install with 'pip install Mako' or the extra 'botmark[mako]'."
                return strip_func( MakoTemplate(content).render(**data))

        elif lang == "jinja2" and isinstance(data, dict):
            try:
                from jinja2 import Template as JinjaTemplate
            except ImportError:
                return "⚠️  'Jinja2' is not installed; install with 'pip install Jinja2' or the extra 'botmark[jinja2]'."
            return strip_func( JinjaTemplate(content).render(**data))

        elif lang == "fstring":
            # Allow `{...}` expressions without requiring a leading f in user input
            try:
                return strip_func( render_fstring(content, context))
            except Exception as e:
                return f"⚠️ fstring render error: {e}"

        elif lang in ("format", "str.format"):
            try:
                return strip_func( render_format(content, context))
            except KeyError as e:
                return f"⚠️ format placeholder not found in context: {e}"
            except Exception as e:
                return f"⚠️ format render error: {e}"

    except Exception as e:
        return str(e)

    # Fallback: return raw content unchanged
    return content

def render_named_block(name, blocks, system, header, version, query, topics, images, links, mcp_servers, venv_base_dir, data={} ):
    template_data = {
        #"BLOCKS": {key: obj.to_json() for key, obj in blocks.items() if obj is not None},
        "BLOCKS": {key: obj for key, obj in blocks.items() if obj is not None},        
        "TOPICS": topics,
        "IMAGES": images,
        "LINKS": links,
        "MCP_SERVERS": mcp_servers,
        "SYSTEM": system,
        "HEADER": header,
        "VERSION": version,
        "QUERY": query
    }
    block = get_block(name, blocks)
    return render_block(block, template_data | data, venv_base_dir) if block is not None else ""

def get_tools( blocks ):

    tools = []
    for _, block in blocks.items():
        if block.get("language") == "python" and "tool" in block.get("classes"):
            tools.append( {"code": block.get("content"), "attributes": block.get("attributes")} )
    return tools

def get_tests( blocks ):
    for block in blocks:
        print ( block )


###### get_blocks 
class RemoteFetchError(Exception):
    """Raised when fetching a remote file fails."""

def read_file_content(file_path: str, timeout: float = 10, is_binary: bool = False) -> Optional[Union[str, bytes]]:
    """
    Read content from a local or remote file.

    - If `file_path` starts with http(s), fetch it over the network (using a lazy import of `requests`).
    - Otherwise, read it from disk. If a relative path doesn't exist, also try resolving it
      relative to the installed `botmark` package directory.

    Args:
        file_path: Path or URL of the file to read.
        timeout:   Timeout in seconds for both local read (via thread) and HTTP GET.
        is_binary: If True, return bytes; otherwise return str (UTF-8 for local files).

    Returns:
        The file content (str or bytes) on success, or None on failure.
    """

    def read_local_file():
        def get_botmark_dir():
            spec = importlib.util.find_spec("botmark")
            if spec and spec.origin:
                return os.path.dirname(spec.origin)
            raise ImportError("botmark package not found")

        logger.debug("Trying to read file:", file_path)

        # Try the direct path first
        if os.path.exists(file_path):
            target_path = file_path
        else:
            # If not found and the path is relative, try resolving relative to botmark
            if not os.path.isabs(file_path):
                try:
                    botmark_dir = get_botmark_dir()
                    alt_path = os.path.join(botmark_dir, file_path)
                    print("[DEBUG] Trying alternate path:", alt_path)
                    if os.path.exists(alt_path):
                        target_path = alt_path
                    else:
                        raise FileNotFoundError(f"File not found: {file_path} or {alt_path}")
                except ImportError as e:
                    print(e)
                    raise FileNotFoundError(f"File not found: {file_path} (botmark dir not found)")
            else:
                raise FileNotFoundError(f"File not found: {file_path}")

        mode = "rb" if is_binary else "r"
        kwargs = {} if is_binary else {"encoding": "utf-8"}

        with open(target_path, mode, **kwargs) as f:
            return f.read()

    def read_remote_file():
        try:
            import requests  # Lazy import so the dependency is optional
        except ImportError as e:
            raise RemoteFetchError(
                "The 'requests' package is required to read remote URLs but is not installed."
            ) from e

        try:
            response = requests.get(file_path, timeout=timeout)
            response.raise_for_status()
            return response.content if is_binary else response.text
        except Exception as e:
            # Don’t leak requests-specific types to the outer scope
            raise RemoteFetchError(str(e)) from e

    try:
        if file_path.startswith(("http://", "https://")):
            return read_remote_file()
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(read_local_file)
                return future.result(timeout=timeout)

    except FileNotFoundError as e:
        print(e)
    except concurrent.futures.TimeoutError:
        print(f"Error: Reading file timed out: {file_path}")
    except RemoteFetchError as e:
        print(f"Error fetching file from URL: {file_path} - {e}")
    except Exception as e:
        print(f"Error reading file: {file_path} - {e}")

    return None

def parse_data_url(data_url):
    # Remove the 'data:' prefix
    if not data_url.startswith('data:'):
        raise ValueError("Invalid data URL")
    
    # Split the URL into metadata and data
    try:
        metadata, data = data_url[5:].split(',', 1)
    except ValueError:
        raise ValueError("Malformed data URL")
    
    # Check if the data is base64 encoded
    if ';base64' in metadata:
        raise ValueError("Base64-encoded data URLs are not supported in this implementation")
    
    # Decode the percent-encoded data
    decoded_data = urllib.parse.unquote(data)
    
    # Parse the JSON content
    try:
        json_content = json.loads(decoded_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON content: {e}")
    
    return json_content

def get_lambda(lambda_str: str, default_lambda = lambda x:x):
    try:
        lambda_func = eval(lambda_str.strip())  # Convert string to lambda function
        if callable(lambda_func):
            return lambda_func
        print("Provided string is not a valid lambda function")    
    except Exception as e:
        print( f"Error: {e}")
    return default_lambda

def yaml_to_json(yaml_string):
    try:
        yaml_data = yaml.safe_load(yaml_string)
        return yaml_data
    except yaml.YAMLError as e:
        return {"error": str(e) }
    
def find_reader_by_extension(extension, readers):
    for reader_data in readers:
        extensions = reader_data.get("attributes", {}).get("extensions", "")
        ext_list = extensions.split()
        if extension in ext_list:
            return reader_data
    return None

def get_graph(graphs, ranking_function: callable = lambda x: 0  ):
    graph  = None
    score = -1
    for g in graphs:
        block_score = ranking_function(g)
        if block_score > score:
            graph = g
            score = block_score
    return graph

def get_blocks(blocks, ranking_function: callable = lambda x: 0 ):

    valid_blocks = {}
    scores = {}
    for block in blocks:
        block_id = block.get("attributes", {}).get("id")
        if not block_id:
            continue

        codeblock = CodeBlock(**block)

        score = ranking_function(codeblock)
        if score >= 0 and score >= scores.get( block_id, -1 ):
            valid_blocks[block_id] = codeblock
            scores [block_id] = score

    block_loaders = {
        'json': json.loads,
        'yaml': yaml.safe_load
    }

    # apply transforms
    for key, block in valid_blocks.items():
        content = block.get("content")
        language = block.get("language")
        
        if language in block_loaders:
            content = block_loaders[language]( content )
    
        valid_blocks[key] = CodeBlock( **block.data | {"content": content } )
    return valid_blocks

def try_answer(blocks, system, header, version, query, venv_base_dir, topics, images, links, mcp_servers ):
    if "response" in blocks and not "RESPONSE" in blocks["response"].get("content", ""):
        return render_named_block("response", blocks, system, header, version, query, topics, images, links, mcp_servers, venv_base_dir)
    return None

def dumps( data ):
    return json.dumps( data, indent = 4, ensure_ascii=False)

def make_answer( blocks, system, header, version, query, text, venv_base_dir, topics={}, images=[], links=[], mcp_servers = [] ):
    json_response = { "RESPONSE": text }
    response_text = text
    if "schema" in blocks:
        try:
            response_data = json.loads( text )
            json_response["RESPONSE"] = response_data
            response_text = "```json\n" + dumps( response_data ) + "\n```"
        except Exception as e:
            print (str(e))
            response_text = str(e)

    if "response" in blocks:
        try:
            response_text = render_named_block( "response", blocks, system, header, version, query, topics, images, links, mcp_servers, venv_base_dir, json_response )    
        except Exception as e:
            response_text = str(e)
    return response_text

def parse_markdown_to_qa_pairs(md_text: str):
    """
    Parse simple QA markdown:
      - Questions: lines starting with '#'
      - Answers:   lines starting with '>'
    Behavior:
      - Each '>' line produces its OWN qa pair with the current question.
      - HTML comments <!-- ... --> (single or multi-line) are removed first.
    Returns: list[{"question": str, "answer": str|None}]
    """

    # Remove HTML comments (single- and multi-line)
    without_comments = re.sub(r'<!--.*?-->', '', md_text, flags=re.DOTALL)

    lines = without_comments.strip().splitlines()

    qa_pairs = []
    current_question = None
    # We no longer need to buffer multi-line answers; each '>' line is its own test.

    for raw in lines:
        line = raw.strip()
        if not line:
            # blank lines do not finalize anything now
            continue

        if line.startswith("#"):
            # New question header (strip leading '#')
            current_question = line.lstrip("#").strip()
            continue

        if line.startswith(">"):
            # One answer line => one qa_pair
            if current_question is None:
                # No question yet; skip or treat as orphan. We skip to be safe.
                continue
            answer = line.lstrip(">").strip()
            qa_pairs.append({"question": current_question, "answer": answer})
            continue

        # Any other line type is ignored in this minimal dialect

    # No trailing flush needed because answers are emitted immediately
    return qa_pairs

class NextOption(NamedTuple):
    node_id: str
    label: Optional[str]  # Edge label (source -> node_id), if present


def unique_next_options_for_prefix(
    valid_paths: List[List[str]],
    edge_label: Dict[Tuple[str, str], Optional[str]],
    prefix: List[str],
) -> List[NextOption]:
    """Determines all unique NextOptions for the current path prefix."""
    opts: List[NextOption] = []
    plen = len(prefix)
    for vp in valid_paths:
        if len(vp) > plen and vp[:plen] == prefix:
            nxt = vp[plen]
            if all(o.node_id != nxt for o in opts):
                opts.append(
                    NextOption(
                        node_id=nxt,
                        label=edge_label.get((prefix[-1], nxt)),
                    )
                )
    return opts


def make_edge_choice_model(allowed_nodes: List[str]):
    """Creates a Pydantic model at runtime with node_id constrained to the allowed options."""
    try:
        from pydantic import create_model, Field
    except ImportError:
         raise SystemExit("❌ 'pydantic' is not installed. Please install with `pip install pydantic`.")

    NodeEnum = Enum("NodeEnum", {f"opt_{i}": nid for i, nid in enumerate(allowed_nodes)})
    return create_model(
        "EdgeChoiceDynamic",
        node_id=(NodeEnum, Field(..., description="The chosen node_id from the allowed options.")),
        rationale=(str, Field(..., description="A short justification for the choice (1–2 sentences).")),
    )


# ---------------------------
# Async graph traversal with per-agent histories + flat transcript + final answer
# ---------------------------

async def traverse_graph(
    graph_obj: Dict[str, Any],
    processors: Dict[str, Any],
    *,
    initial_history: Optional[List[Any]] = None,
    start_message: str = "Hello, let's start the conversation.",
    runner: Optional[Any] = None,
) -> Tuple[Dict[str, List[Any]], List[str], str]:
    """
    Async traversal:
    - each agent receives the previous agent's answer as input
    - one pre-history (initial_history) is copied to EVERY agent's history
    - internal router uses ONLY runner and sees the current node's history
    Returns: (histories per agent, transcript of node names, final answer)
    """
    # Seed per-agent histories with the SAME initial history (copied per agent)
    histories: Dict[str, List[Any]] = {
        node: (list(initial_history) if initial_history else [])
        for node in processors
    }

    valid_paths: List[List[str]] = graph_obj.get("valid_paths", [])

    if not valid_paths or not valid_paths[0]:
        return histories, [], start_message

    edges = graph_obj.get("graph", {}).get("edges", [])
    edge_label: Dict[Tuple[str, str], Optional[str]] = {
        (e["source"], e["target"]): e.get("label") for e in edges
    }

    # Start at the first node of the first valid path
    path_so_far: List[str] = [valid_paths[0][0]]
    current = path_so_far[-1]

    transcript: List[str] = []
    last_output = start_message  # becomes final answer after the loop

    # --- Internal async selection (router) using ONLY selection_model ---
    async def selection(
        current_node_id: str,
        options: List[NextOption],
        path_prefix: List[str],
        hists: Dict[str, List[Any]],
    ) -> Optional[NextOption]:
        
        if not options:
            return None
        
        # exactly one option → skip LLM/router entirely
        if len(options) == 1:
            return options[0]
        
        allowed_ids = [o.node_id for o in options]
        EdgeChoiceDynamic = make_edge_choice_model(allowed_ids)

        def _options_to_dict(opts: List[NextOption]):
            return [{"node_id": o.node_id, "label": o.label} for o in opts]
        
        system_prompt= """
You are a router agent. Choose exactly ONE of the allowed options based on the given goals.
Respond strictly as JSON that is valid for the Pydantic schema EdgeChoiceDynamic.
If multiple options are reasonable, prefer the one that provides new information
or continues the current path. NEVER choose a node_id that is not in the provided options."""

        prompt = {
            "current_node": current_node_id,
            "path_so_far": path_prefix,
            "options": _options_to_dict(options),
            "instruction": (
                "Choose exactly one option from 'options' and return its node_id. "
                "The node_id must be one of the provided options."
            ),
        }

        try:
            res = await runner( json.dumps(prompt), system_prompt= system_prompt, output_type=EdgeChoiceDynamic, message_history=hists.get(current_node_id, []) )
            chosen_id = res.output["node_id"]["value"]
        except Exception as e:
            print("Router exception, falling back to first option:", e)
            chosen_id = allowed_ids[0]

        option_map = {o.node_id: o for o in options}
        return option_map.get(chosen_id, options[0])

    # ---------------- Main traversal loop (async) ----------------
    def next_options_for_prefix(prefix: List[str]) -> List[NextOption]:
        return unique_next_options_for_prefix(valid_paths, edge_label, prefix)

    while True:

        # 1) Run the current node's agent with the previous agent's output
        agent = processors.get(current)

        if agent is not None and hasattr(agent, "run"):
            result = await agent.run(
                last_output,
                message_history=histories[current],  # starts with initial_history
            )
            #histories[current] += result.new_messages()
            histories[current] = result.all_messages

            last_output = result.output             # <- keep updating; becomes final answer
            transcript.append(current)              # record the node/agent name

        # 2) Determine next-step options
        options = next_options_for_prefix(path_so_far)
        if not options:
            break  # end of path; last_output is final answer

        # 3) Internal selection using ONLY selection_model (async)
        choice = await selection(current, options, path_so_far[:], histories)
        if choice is None:
            break
        if all(choice.node_id != o.node_id for o in options):
            raise ValueError(
                f"Selection chose invalid next node '{choice}'. "
                f"Allowed: {[o.node_id for o in options]}"
            )

        # 4) Advance
        path_so_far.append(choice.node_id)
        current = choice.node_id

    answer = last_output
    return histories, transcript, answer
