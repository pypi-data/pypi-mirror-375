import pytest, os
from botmark.config import Settings

def test_env_file_defaults():
    """Ensure values from .env.test are applied."""
    assert Settings.FRAMEWORK_NAME == "pydantic-ai"
    assert Settings.FRAMEWORK_CONFIG == {}
    assert Settings.VENV_BASE_DIR == "/tmp/venvs"
