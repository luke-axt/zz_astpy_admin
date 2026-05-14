import json
import time
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from ..auth import verify_team_key
from ..config import resolve_model
from ..db import log_request
from ..models import ChatCompletionRequest, ChatCompletionResponse, ModelsResponse, ModelInfo
from ..openai_client import chat_completions, stream_chat_completions

router = APIRouter()


@router.post("/v1/chat/completions")
async def openai_chat_completions(
    request: Request,
    body: ChatCompletionRequest,
    user: str = Depends(verify_team_key),
):
    real_model = resolve_model(body.model)
    body.model = real_model

    start = time.time()
    endpoint = "/openai/v1/chat/completions"

    if body.stream:
        async def _stream() -> AsyncGenerator[str, None]:
            prompt_tokens = 0
            completion_tokens = 0
            status_code = 200
            try:
                async for line in stream_chat_completions(body):
                    # Try to extract usage from final chunk
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str != "[DONE]":
                            try:
                                chunk = json.loads(data_str)
                                usage = chunk.get("usage")
                                if usage:
                                    prompt_tokens = usage.get("prompt_tokens", 0)
                                    completion_tokens = usage.get("completion_tokens", 0)
                            except json.JSONDecodeError:
                                pass
                    yield line
            except Exception:
                status_code = 500
                raise
            finally:
                duration_ms = int((time.time() - start) * 1000)
                await log_request(
                    user=user,
                    endpoint=endpoint,
                    model=real_model,
                    status_code=status_code,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    duration_ms=duration_ms,
                )

        return StreamingResponse(
            _stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    status_code = 200
    prompt_tokens = 0
    completion_tokens = 0
    try:
        resp = await chat_completions(body)
        status_code = resp.status_code
        data = resp.json()

        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        return data
    except Exception:
        status_code = 500
        raise
    finally:
        duration_ms = int((time.time() - start) * 1000)
        await log_request(
            user=user,
            endpoint=endpoint,
            model=real_model,
            status_code=status_code,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            duration_ms=duration_ms,
        )


@router.get("/v1/models")
async def openai_models(
    user: str = Depends(verify_team_key),
):
    from ..config import get_yaml_config
    models = get_yaml_config().get("models", {})
    data = [
        ModelInfo(id=alias)
        for alias in models.keys()
    ]
    return ModelsResponse(data=data)
