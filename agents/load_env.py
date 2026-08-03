"""Carrega .env da raiz do projeto e do cwd."""

from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


def load() -> None:
    load_dotenv(ROOT / ".env")
    load_dotenv()
