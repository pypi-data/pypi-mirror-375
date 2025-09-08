from __future__ import annotations
import json
import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_BASE_URL = os.environ.get("ORCHAGENT_BASE_URL", "http://localhost:8080")
TOKEN_PATH = Path(os.environ.get("ORCHAGENT_TOKEN_FILE", Path.home() / ".orchagent" / "token.json"))


@dataclass
class Settings:
    base_url: str = DEFAULT_BASE_URL
    token_path: Path = TOKEN_PATH
    timeout_seconds: float = float(os.environ.get("ORCHAGENT_TIMEOUT", "30"))

    @classmethod
    def ensure_dirs(cls, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

