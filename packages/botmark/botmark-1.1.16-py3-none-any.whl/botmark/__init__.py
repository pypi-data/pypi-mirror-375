import importlib.metadata, uuid, logging
from .utils.logging import setup_logging, set_request_id

try:
    __version__ = importlib.metadata.version("botmark")
except:
    __version__ = "0.0.0+local"

logger = setup_logging(name="botmark", level=logging.NOTSET)
set_request_id(str(uuid.uuid4()))

from .core import BotManager, BotMarkAgent, FileSystemSource, BotmarkSource, StringSource, create_ai_runner, Runner, parse_to_json
from .config import Settings

__all__ = ["BotManager", "BotMarkAgent", "FileSystemSource", "BotmarkSource", "StringSource", "create_ai_runner", "Runner", "parse_to_json"]
