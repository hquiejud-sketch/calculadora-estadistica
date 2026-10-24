"""Configuración leída del archivo .env."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "datos" / "estadistica.db"))
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"


def ia_configurada() -> bool:
    return bool(GEMINI_API_KEY) and not GEMINI_API_KEY.startswith("pon_aqui")
