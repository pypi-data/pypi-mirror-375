from __future__ import annotations
import json
from typing import Any, Dict, Optional, Iterable
import httpx

from .config import Settings
from .auth import TokenStore
from .errors import Unauthorized, Forbidden, NotFound, RateLimited, ServerError
from .models import ThreadCreateResponse, RunStartResponse, Event, HistoryItem


class OrchClient:
    def __init__(self, base_url: Optional[str] = None, settings: Optional[Settings] = None) -> None:
        self.settings = settings or Settings(base_url=base_url or Settings().base_url)
        self._client = httpx.Client(base_url=self.settings.base_url, timeout=self.settings.timeout_seconds)
        self._token_store = TokenStore(self.settings)
        self._token: Optional[str] = self._token_store.load()

    # ---------- internals ----------
    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.status_code == 401:
            raise Unauthorized(resp.text)
        if resp.status_code == 403:
            raise Forbidden(resp.text)
        if resp.status_code == 404:
            raise NotFound(resp.text)
        if resp.status_code == 429:
            raise RateLimited(resp.text)
        if resp.status_code >= 500:
            raise ServerError(resp.text)
        resp.raise_for_status()

    # ---------- auth ----------
    class _Auth:
        def __init__(self, outer: "OrchClient") -> None:
            self._outer = outer

        def register(self, email: str, password: str, profile: Optional[Dict[str, Any]] = None, save: bool = True) -> str:
            body = {"email": email, "password": password}
            if profile:
                body["profile"] = profile
            resp = self._outer._client.post("/auth/register", json=body, headers={"Content-Type": "application/json"})
            self._outer._raise_for_status(resp)
            token = resp.json().get("access_token")
            if save and token:
                self._outer._token = token
                self._outer._token_store.save(token)
            return token

        def login(self, email: str, password: str, save: bool = True) -> str:
            resp = self._outer._client.post("/auth/login", json={"email": email, "password": password}, headers={"Content-Type": "application/json"})
            self._outer._raise_for_status(resp)
            token = resp.json().get("access_token")
            if save and token:
                self._outer._token = token
                self._outer._token_store.save(token)
            return token

        def set_token(self, token: str, save: bool = True) -> None:
            self._outer._token = token
            if save:
                self._outer._token_store.save(token)

        def get_token(self) -> Optional[str]:
            return self._outer._token

    @property
    def auth(self) -> _Auth:
        return OrchClient._Auth(self)

    # ---------- meta ----------
    def get_meta(self) -> Dict[str, Any]:
        resp = self._client.get("/meta", headers={"Content-Type": "application/json"})
        self._raise_for_status(resp)
        return resp.json()

    # ---------- threads ----------
    class _Threads:
        def __init__(self, outer: "OrchClient") -> None:
            self._outer = outer

        def create(self, spec: Dict[str, Any]) -> str:
            resp = self._outer._client.post("/threads", headers=self._outer._headers(), json=spec)
            self._outer._raise_for_status(resp)
            return ThreadCreateResponse.model_validate(resp.json()).id

        def create_from_file(self, path: str) -> str:
            spec = json.loads(open(path, "r", encoding="utf-8").read())
            return self.create(spec)

        def set_secrets(self, thread_id: str, secrets: Dict[str, Any]) -> None:
            resp = self._outer._client.post(f"/threads/{thread_id}/secrets", headers=self._outer._headers(), json={"secrets": secrets})
            self._outer._raise_for_status(resp)

        def history(self, thread_id: str, limit: int = 20) -> Iterable[HistoryItem]:
            resp = self._outer._client.get(f"/threads/{thread_id}/history", headers=self._outer._headers(), params={"limit": limit})
            self._outer._raise_for_status(resp)
            data = resp.json().get("items", [])
            for it in data:
                yield HistoryItem.model_validate(it)

    @property
    def threads(self) -> _Threads:
        return OrchClient._Threads(self)

    # ---------- runs ----------
    class _Runs:
        def __init__(self, outer: "OrchClient") -> None:
            self._outer = outer

        def send_message(self, thread_id: str, user_prompt: str, inputs: Optional[Dict[str, Any]] = None, secrets: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            body: Dict[str, Any] = {"user_prompt": user_prompt}
            if inputs:
                body["inputs"] = inputs
            if secrets:
                body["secrets"] = secrets
            resp = self._outer._client.post(f"/threads/{thread_id}/messages", headers=self._outer._headers(), json=body)
            self._outer._raise_for_status(resp)
            return RunStartResponse.model_validate(resp.json()).model_dump()

        def stream_events(self, run_id: str) -> Iterable[Dict[str, Any]]:
            with self._outer._client.stream("GET", f"/runs/{run_id}/events", headers=self._outer._headers(), timeout=None) as resp:
                self._outer._raise_for_status(resp)
                for line in resp.iter_lines():
                    if not line:
                        continue
                    if isinstance(line, bytes):
                        try:
                            line = line.decode("utf-8", errors="ignore")
                        except Exception:
                            continue
                    if not line.startswith("data: "):
                        continue
                    data = line[len("data: "):]
                    try:
                        evt = json.loads(data)
                    except Exception:
                        continue
                    yield evt

        def resume(self, run_id: str) -> Dict[str, Any]:
            resp = self._outer._client.post(f"/runs/{run_id}/resume", headers=self._outer._headers(), json={})
            self._outer._raise_for_status(resp)
            return resp.json()

    @property
    def runs(self) -> _Runs:
        return OrchClient._Runs(self)

    # ---------- approvals ----------
    class _Approvals:
        def __init__(self, outer: "OrchClient") -> None:
            self._outer = outer

        def approve(self, run_id: str, tool: str, server: str = "mcp", args_keys: Optional[list[str]] = None) -> Dict[str, Any]:
            body = {"server": server, "tool": tool, "args_keys": args_keys or []}
            resp = self._outer._client.post(f"/approvals/{run_id}/approve", headers=self._outer._headers(), json=body)
            self._outer._raise_for_status(resp)
            return resp.json()

        def clear(self, all: bool = False, user_id: Optional[str] = None) -> Dict[str, Any]:
            body: Dict[str, Any] = {}
            if all:
                body["all"] = True
            if user_id:
                body["user_id"] = user_id
            resp = self._outer._client.post("/approvals/clear", headers=self._outer._headers(), json=body)
            self._outer._raise_for_status(resp)
            return resp.json()

    @property
    def approvals(self) -> _Approvals:
        return OrchClient._Approvals(self)
