from __future__ import annotations
import json
from typing import Optional
from .config import Settings


class TokenStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def save(self, token: str) -> None:
        Settings.ensure_dirs(self.settings.token_path)
        self.settings.token_path.write_text(json.dumps({"access_token": token}), encoding="utf-8")
        try:
            self.settings.token_path.chmod(0o600)
        except Exception:
            pass

    def load(self) -> Optional[str]:
        if not self.settings.token_path.exists():
            return None
        try:
            data = json.loads(self.settings.token_path.read_text(encoding="utf-8"))
            return data.get("access_token")
        except Exception:
            return None

