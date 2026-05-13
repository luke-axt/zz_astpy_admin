import json
from typing import AsyncGenerator

import httpx
from fastapi import HTTPException

from .config import get_settings
from .models import ChatCompletionRequest

_settings = get_settings()

_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=_settings.openai_base_url,
            headers={"Authorization": f"Bearer {_settings.openai_api_key}"},
            timeout=httpx.Timeout(60.0, connect=10.0),
        )
    return _client


async def close_client():
    global _client
    if _client:
        await _client.aclose()
        _client = None


def _build_payload(request: ChatCompletionRequest) -> dict:
    payload = {
        "model": request.model,
        "messages": [m.model_dump() for m in request.messages],
        "stream": request.stream,
    }
    if request.temperature is not None:
        payload["temperature"] = request.temperature
    if request.top_p is not None:
        payload["top_p"] = request.top_p
    if request.max_tokens is not None:
        payload["max_tokens"] = request.max_tokens
    if request.tools is not None:
        payload["tools"] = request.tools
    if request.tool_choice is not None:
        payload["tool_choice"] = request.tool_choice
    if request.stop is not None:
        payload["stop"] = request.stop
    if request.frequency_penalty is not None:
        payload["frequency_penalty"] = request.frequency_penalty
    if request.presence_penalty is not None:
        payload["presence_penalty"] = request.presence_penalty
    if request.user is not None:
        payload["user"] = request.user
    if request.stream:
        payload["stream_options"] = {"include_usage": True}
    return payload


async def chat_completions(request: ChatCompletionRequest) -> httpx.Response:
    client = get_client()
    payload = _build_payload(request)
    try:
        resp = await client.post("/chat/completions", json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Upstream timeout") from exc
    except httpx.NetworkError as exc:
        raise HTTPException(status_code=502, detail="Upstream network error") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=exc.response.text,
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upstream error: {exc}") from exc


async def stream_chat_completions(request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
    client = get_client()
    payload = _build_payload(request)
    try:
        async with client.stream("POST", "/chat/completions", json=payload) as resp:
            if resp.status_code != 200:
                text = await resp.aread()
                raise HTTPException(status_code=resp.status_code, detail=text.decode("utf-8", errors="replace"))
            async for line in resp.aiter_lines():
                if line.strip():
                    yield line + "\n"
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Upstream timeout") from exc
    except httpx.NetworkError as exc:
        raise HTTPException(status_code=502, detail="Upstream network error") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upstream error: {exc}") from exc
