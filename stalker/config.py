"""Configuration loader from .env and environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


class Config:
    EXIFTOOLS_API_KEY = os.getenv("EXIFTOOLS_API_KEY", "")
    NUMVERIFY_API_KEY = os.getenv("NUMVERIFY_API_KEY", "")
    VERIPHONE_API_KEY = os.getenv("VERIPHONE_API_KEY", "")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    DORK_MAX_RESULTS = int(os.getenv("DORK_MAX_RESULTS", "20"))
    MAIGRET_TIMEOUT = int(os.getenv("MAIGRET_TIMEOUT", "60"))
    MAIGRET_MAX_SITES = int(os.getenv("MAIGRET_MAX_SITES", "500"))
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(BASE_DIR / "output")))
    IMAGE_DIR = Path(os.getenv("IMAGE_DIR", str(BASE_DIR / "output" / "images")))
    STEALTH_MODE = os.getenv("STEALTH_MODE", "false").lower() in ("true", "1", "yes")
    STEALTH_RANDOM_UA = os.getenv("STEALTH_RANDOM_UA", "true").lower() in ("true", "1", "yes")
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.5"))
    FACE_SEARCH_MAX_AVATARS = int(os.getenv("FACE_SEARCH_MAX_AVATARS", "3"))
    LOCALDB_DIR = os.getenv("LOCALDB_DIR", str(BASE_DIR.parent / "databaselocal"))

    @classmethod
    def ensure_dirs(cls):
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.IMAGE_DIR.mkdir(parents=True, exist_ok=True)
