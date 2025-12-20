from __future__ import annotations

import json
import os
from typing import Literal, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import DATA_DIR


KEYS_PATH = DATA_DIR / "api_keys.json"


def _read_keys() -> dict:
    if not KEYS_PATH.exists():
        return {}
    try:
        return json.loads(KEYS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_keys(keys: dict) -> None:
    KEYS_PATH.parent.mkdir(parents=True, exist_ok=True)
    KEYS_PATH.write_text(json.dumps(keys, indent=2), encoding="utf-8")


class KeysPayload(BaseModel):
    gemini: Optional[str] = Field(default=None)
    claude: Optional[str] = Field(default=None)
    openai: Optional[str] = Field(default=None)


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    model: Literal["gemini", "claude", "gpt4"]
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    content: str


app = FastAPI(title="Sovwren Web API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/keys/status")
def keys_status() -> dict:
    keys = _read_keys()
    return {
        "gemini": bool(keys.get("gemini") or os.environ.get("GEMINI_API_KEY")),
        "claude": bool(keys.get("claude") or os.environ.get("ANTHROPIC_API_KEY")),
        "openai": bool(keys.get("openai") or os.environ.get("OPENAI_API_KEY")),
    }


@app.post("/api/keys")
def set_keys(payload: KeysPayload) -> dict:
    keys = _read_keys()
    update = payload.model_dump(exclude_unset=True)

    # Store only provided keys; allow clearing with empty string.
    for k, v in update.items():
        if v is None:
            continue
        keys[k] = v.strip()

    _write_keys(keys)
    return {"ok": True}


async def _call_gemini(messages: list[ChatMessage]) -> str:
    keys = _read_keys()
    api_key = (keys.get("gemini") or os.environ.get("GEMINI_API_KEY") or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API key missing (set in /api/keys or GEMINI_API_KEY)")

    prompt = messages[-1].content if messages else ""
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Empty prompt")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {
        "Content-Type": "application/json",
        # Avoid putting keys in URLs; URLs leak everywhere.
        "x-goog-api-key": api_key,
    }
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, json=body)
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise HTTPException(status_code=resp.status_code, detail=str(detail))

        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            raise HTTPException(status_code=502, detail="Unexpected Gemini response format")


async def _call_claude(messages: list[ChatMessage]) -> str:
    keys = _read_keys()
    api_key = (keys.get("claude") or os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="Anthropic API key missing (set in /api/keys or ANTHROPIC_API_KEY)")

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 1024,
        "messages": [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role != "system"
        ],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, headers=headers, json=body)
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise HTTPException(status_code=resp.status_code, detail=str(detail))

        data = resp.json()
        try:
            return data["content"][0]["text"]
        except Exception:
            raise HTTPException(status_code=502, detail="Unexpected Anthropic response format")


async def _call_openai(messages: list[ChatMessage]) -> str:
    keys = _read_keys()
    api_key = (keys.get("openai") or os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key missing (set in /api/keys or OPENAI_API_KEY)")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "gpt-4o",
        "messages": [{"role": m.role, "content": m.content} for m in messages],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, headers=headers, json=body)
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise HTTPException(status_code=resp.status_code, detail=str(detail))

        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            raise HTTPException(status_code=502, detail="Unexpected OpenAI response format")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    if req.model == "gemini":
        content = await _call_gemini(req.messages)
    elif req.model == "claude":
        content = await _call_claude(req.messages)
    elif req.model == "gpt4":
        content = await _call_openai(req.messages)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown model: {req.model}")

    return ChatResponse(content=content)
