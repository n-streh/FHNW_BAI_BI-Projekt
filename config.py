import os
from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parent / ".env"


def _load_env_file(env_path: Path) -> None:
    """Minimaler .env-Parser als Fallback ohne python-dotenv."""
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


try:
    from dotenv import load_dotenv

    load_dotenv(_ENV_PATH)
except ImportError:
    _load_env_file(_ENV_PATH)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Startup.6")
DB_NAME = os.getenv("DB_NAME", "flughafendb_large")
