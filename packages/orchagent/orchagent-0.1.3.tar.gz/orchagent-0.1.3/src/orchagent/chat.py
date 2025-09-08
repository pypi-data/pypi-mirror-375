from __future__ import annotations
from typing import Any, Dict, Iterable, Optional
from .client import OrchClient


class ChatSession:
    def __init__(self, client: OrchClient, thread_id: str) -> None:
        self.client = client
        self.thread_id = thread_id

    def ask(self, prompt: str, *, inputs: Optional[Dict[str, Any]] = None, secrets: Optional[Dict[str, Any]] = None) -> Iterable[Dict[str, Any]]:
        run = self.client.runs.send_message(self.thread_id, user_prompt=prompt, inputs=inputs, secrets=secrets)
        run_id = run["run_id"]
        return self.client.runs.stream_events(run_id)

