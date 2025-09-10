import os
import json
import logging
from typing import Optional, Dict, Any

from .runners import is_valid_config

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    pass

class Settings:
    FRAMEWORK_NAME: Optional[str] = None
    FRAMEWORK_CONFIG: Optional[Dict[str, Any]] = None
    TELEMETRY: Optional[Dict[str, Any]] = None
    VENV_BASE_DIR: str = "/data/venvs"

    @classmethod
    def load(cls) -> None:
        prefix = "BM_"

        # 1) VENV base dir
        cls.VENV_BASE_DIR = os.getenv(f"{prefix}VENV_BASE_DIR", cls.VENV_BASE_DIR)

        # 2) Read raw envs first
        fw_raw = os.getenv(f"{prefix}FRAMEWORK_NAME")          # None if unset
        cfg_raw = os.getenv(f"{prefix}FRAMEWORK_CONFIG")       # None if unset
        tel_raw = os.getenv(f"{prefix}TELEMETRY")              # None if unset

        try:
            cls.TELEMETRY = json.loads(tel_raw)
        except:
            cls.TELEMETRY = tel_raw

        # 3) Parse JSON config only if provided; let cfg be None if not set
        cfg: Optional[Dict[str, Any]]
        if cfg_raw is None:
            cfg = None
        else:
            try:
                parsed = json.loads(cfg_raw)
                if not isinstance(parsed, dict):
                    raise ConfigError(f"{prefix}FRAMEWORK_CONFIG must be a JSON object")
                cfg = parsed
            except json.JSONDecodeError as e:
                raise ConfigError(f"Invalid JSON in {prefix}FRAMEWORK_CONFIG: {e}") from e
            
        # 4) If one is missing, log clearly and leave class attrs as defaults
        missing = []
        if not fw_raw:
            missing.append(f"{prefix}FRAMEWORK_NAME")
        if cfg is None:
            missing.append(f"{prefix}FRAMEWORK_CONFIG")
        if missing:
            logger.warning("Missing required env var(s): %s", ", ".join(missing))
            return

        # 5) Validate, then set
        if is_valid_config(fw_raw, cfg):
            cls.FRAMEWORK_NAME = fw_raw
            cls.FRAMEWORK_CONFIG = cfg
            logger.info("Settings loaded (framework=%s, venv_base_dir=%s)", fw_raw, cls.VENV_BASE_DIR)
        else:
            logger.warning(f"Invalid configuration for framework '{fw_raw}'")

Settings.load()