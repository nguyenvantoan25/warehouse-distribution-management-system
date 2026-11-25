"""Backend-owned configuration; environment variables take precedence over .env."""

import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env", override=False)
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://distriflow@127.0.0.1:55432/distriflow"
)
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
