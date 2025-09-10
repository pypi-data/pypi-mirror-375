import os
from pathlib import Path
from dotenv import load_dotenv

def pytest_configure(config):
    """Force loading of .env.test for test runs, with visible log output."""
    env_file = Path(__file__).parent / ".env.test"
    if env_file.exists():
        load_dotenv(env_file, override=True)
        print(f"[pytest] ✅ Loaded environment variables from {env_file}")
        # Print some key env vars for confirmation (optional, redact secrets!)
        for key in ("OPENAI_API_KEY", "BOTMARK_ENV", "DOTENV_PATH"):
            if key in os.environ:
                print(f"[pytest]    {key}={os.environ[key]}")
    else:
        print(f"[pytest] ⚠️ No .env.test found at {env_file}")
