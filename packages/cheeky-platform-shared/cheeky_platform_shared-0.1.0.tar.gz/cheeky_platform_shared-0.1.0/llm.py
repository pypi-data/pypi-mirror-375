from __future__ import annotations

from typing import Any

import httpx

try:
    from langsmith import traceable  # type: ignore
except Exception:  # pragma: no cover - optional dependency

    def traceable(*_args, **_kwargs):  # type: ignore
        def _decorator(func):
            return func

        return _decorator


# Settings adapter: attempt to read env directly to avoid backend coupling
import os


def _get(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key)
    if v:
        return v
    # Backend-compatible fallbacks (CHEEKY_*)
    return os.getenv(f"CHEEKY_{key}", default)


def _get_timeout() -> int:
    try:
        return int(os.getenv("CHEEKY_OPENAI_TIMEOUT_SECONDS", "60"))
    except Exception:
        return 60


@traceable(name="openai_chat_structured")
async def openai_chat_structured(system: str, user: str, response_model) -> Any:
    api_key = _get("OPENAI_API_KEY")
    model = _get("OPENAI_MODEL") or _get("OPENAI_MODEL", "gpt-4o-mini")
    base_url = _get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    temperature = float(os.getenv("CHEEKY_OPENAI_TEMPERATURE", "0.0"))
    if not api_key:
        raise RuntimeError("OpenAI API key not configured")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=_get_timeout(), base_url=base_url) as client:
        resp = await client.post("/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        return response_model.model_validate_json(content)


@traceable(name="openai_chat_text")
async def openai_chat_text(system: str, user: str) -> str:
    api_key = _get("OPENAI_API_KEY")
    model = _get("OPENAI_MODEL") or _get("OPENAI_MODEL", "gpt-4o-mini")
    base_url = _get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    temperature = float(os.getenv("CHEEKY_OPENAI_TEMPERATURE", "0.0"))
    if not api_key:
        raise RuntimeError("OpenAI API key not configured")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }

    async with httpx.AsyncClient(timeout=_get_timeout(), base_url=base_url) as client:
        resp = await client.post("/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "") or ""
