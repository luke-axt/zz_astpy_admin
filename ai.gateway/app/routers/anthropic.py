import json
import time
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from ..adapter import (
    anthropic_to_openai_request,
    openai_response_to_anthropic_response,
    openai_stream_to_anthropic_events,
)
from ..auth import verify_team_key
from ..config import resolve_model
from ..db import log_request
from ..models import MessagesRequest
from ..openai_client import chat_completions, stream_chat_completions

router = APIRouter()


@router.post("/v1/messages")
async def anthropic_messages(
    request: Request,
    body: MessagesRequest,
    user: str = Depends(verify_team_key),
):
    start = time.time()
    endpoint = "/anthropic/v1/messages"
    mapped_model = resolve_model(body.model)

    openai_req = anthropic_to_openai_request(body)
    real_model = openai_req.model

    if body.stream:
        async def _stream() -> AsyncGenerator[str, None]:
            prompt_tokens = 0
            completion_tokens = 0
            status_code = 200
            try:
                sse_source = stream_chat_completions(openai_req)
                async for event_line in openai_stream_to_anthropic_events(sse_source, mapped_model):
                    # Extract usage from message_delta events
                    if event_line.startswith("event: message_delta"):
                        try:
                            data_part = event_line.split("\ndata: ", 1)[1]
                            delta_obj = json.loads(data_part)
                            usage = delta_obj.get("usage", {})
                            completion_tokens = usage.get("output_tokens", 0)
                        except Exception:
                            pass
                    yield event_line
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
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            },
        )

    status_code = 200
    prompt_tokens = 0
    completion_tokens = 0
    try:
        resp = await chat_completions(openai_req)
        status_code = resp.status_code
        data = resp.json()

        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        anthropic_data = openai_response_to_anthropic_response(data, mapped_model)
        return anthropic_data
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
