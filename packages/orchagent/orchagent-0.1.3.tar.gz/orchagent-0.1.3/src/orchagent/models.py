from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ThreadCreateResponse(BaseModel):
    id: str


class RunStartResponse(BaseModel):
    run_id: str


class Event(BaseModel):
    type: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


class HistoryItem(BaseModel):
    role: str
    content: str
    meta_json: Optional[str] = None
    created_at: str

