import json
from typing import AsyncGenerator, Any

from .config import resolve_model
from .models import (
    ChatCompletionRequest,
    MessagesRequest,
    MessagesResponse,
    ContentBlock,
)


def _convert_system(system: str | list[dict] | None) -> list[dict]:
    if system is None:
        return []
    if isinstance(system, str):
        return [{"role": "system", "content": system}]
    # list of content blocks
    texts = []
    for block in system:
        if isinstance(block, dict) and block.get("type") == "text":
            texts.append(block.get("text", ""))
    return [{"role": "system", "content": "\n".join(texts)}]


def _convert_messages(anthropic_messages: list[dict]) -> list[dict]:
    openai_messages = []
    for msg in anthropic_messages:
        role = msg.get("role", "")
        content = msg.get("content")
        if isinstance(content, list):
            # Separate different block types
            text_parts = []
            tool_calls = []
            tool_results = []
            for block in content:
                if not isinstance(block, dict):
                    text_parts.append({"type": "text", "text": str(block)})
                    continue
                btype = block.get("type")
                if btype == "text":
                    text_parts.append({"type": "text", "text": block.get("text", "")})
                elif btype == "image":
                    # Preserve image blocks as-is for OpenAI vision
                    text_parts.append(block)
                elif btype == "tool_use":
                    tool_calls.append({
                        "id": block.get("id", ""),
                        "type": "function",
                        "function": {
                            "name": block.get("name", ""),
                            "arguments": json.dumps(block.get("input", {}), ensure_ascii=False),
                        }
                    })
                elif btype == "tool_result":
                    tool_content = block.get("content", "")
                    if isinstance(tool_content, list):
                        texts = [c.get("text", "") for c in tool_content if isinstance(c, dict) and c.get("type") == "text"]
                        tool_content = "\n".join(texts)
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": block.get("tool_use_id", ""),
                        "content": tool_content,
                    })

            # Emit assistant message with text + tool_calls
            if role == "assistant" and (text_parts or tool_calls):
                assistant_msg: dict = {"role": "assistant"}
                if text_parts:
                    assistant_msg["content"] = text_parts if len(text_parts) > 1 else text_parts[0].get("text", "")
                else:
                    assistant_msg["content"] = None
                if tool_calls:
                    assistant_msg["tool_calls"] = tool_calls
                openai_messages.append(assistant_msg)
            elif tool_results:
                for tr in tool_results:
                    openai_messages.append(tr)
            elif text_parts:
                openai_messages.append({"role": role, "content": text_parts})
        else:
            openai_messages.append({"role": role, "content": content})
    return openai_messages


def _convert_tools(tools: list[dict] | None) -> list[dict] | None:
    if not tools:
        return None
    openai_tools = []
    for tool in tools:
        name = tool.get("name", "")
        description = tool.get("description", "")
        input_schema = tool.get("input_schema", {})
        openai_tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": input_schema,
            }
        })
    return openai_tools


def _convert_tool_choice(tool_choice: Any) -> Any:
    if tool_choice is None:
        return None
    if isinstance(tool_choice, str):
        return tool_choice
    if isinstance(tool_choice, dict):
        choice_type = tool_choice.get("type", "auto")
        if choice_type == "auto":
            return "auto"
        if choice_type == "any":
            return "auto"  # OpenAI doesn't have exact "any"; closest approximation
        if choice_type == "tool":
            return {"type": "function", "function": {"name": tool_choice.get("name", "")}}
        if choice_type == "function":
            return tool_choice
    return tool_choice


def anthropic_to_openai_request(req: MessagesRequest) -> ChatCompletionRequest:
    messages = _convert_system(req.system) + _convert_messages(req.messages)
    return ChatCompletionRequest(
        model=resolve_model(req.model),
        messages=[
            {k: v for k, v in m.items() if v is not None}
            for m in messages
        ],
        stream=req.stream,
        temperature=req.temperature,
        top_p=req.top_p,
        max_tokens=req.max_tokens,
        tools=_convert_tools(req.tools),
        tool_choice=_convert_tool_choice(req.tool_choice),
        stop=req.stop_sequences,
    )


def _map_finish_reason(finish_reason: str | None) -> str | None:
    mapping = {
        "stop": "end_turn",
        "length": "max_tokens",
        "tool_calls": "tool_use",
        "content_filter": "end_turn",
    }
    return mapping.get(finish_reason, finish_reason)


def openai_response_to_anthropic_response(openai_data: dict, model: str) -> dict:
    choice = openai_data.get("choices", [{}])[0]
    message = choice.get("message", {})
    content_blocks: list[dict] = []

    text = message.get("content")
    if text:
        content_blocks.append({"type": "text", "text": text})

    tool_calls = message.get("tool_calls")
    if tool_calls:
        for tc in tool_calls:
            func = tc.get("function", {})
            args = func.get("arguments", "{}")
            try:
                input_data = json.loads(args)
            except json.JSONDecodeError:
                input_data = {}
            content_blocks.append({
                "type": "tool_use",
                "id": tc.get("id", ""),
                "name": func.get("name", ""),
                "input": input_data,
            })

    usage = openai_data.get("usage", {})
    anthropic_usage = {
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
    }

    return {
        "id": openai_data.get("id", ""),
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": content_blocks,
        "stop_reason": _map_finish_reason(choice.get("finish_reason")),
        "stop_sequence": None,
        "usage": anthropic_usage,
    }


async def openai_stream_to_anthropic_events(
    sse_lines: AsyncGenerator[str, None],
    model: str,
) -> AsyncGenerator[str, None]:
    """Convert OpenAI SSE stream to Anthropic SSE events."""
    message_id = ""
    sent_message_start = False
    sent_text_block_start = False
    in_tool_call = False
    tool_call_buffer: list[dict] = []
    text_buffer = ""
    finish_reason: str | None = None
    usage_data: dict = {}

    def _flush_text():
        nonlocal text_buffer
        if text_buffer:
            text_buffer = ""

    async for line in sse_lines:
        line = line.strip()
        if not line.startswith("data: "):
            continue
        data_str = line[6:]
        if data_str.strip() == "[DONE]":
            break
        try:
            chunk = json.loads(data_str)
        except json.JSONDecodeError:
            continue

        cid = chunk.get("id", "")
        if cid:
            message_id = cid

        choices = chunk.get("choices", [])
        if not choices:
            # Usage-only chunk at the end (include_usage)
            u = chunk.get("usage")
            if u:
                usage_data = {
                    "input_tokens": u.get("prompt_tokens", 0),
                    "output_tokens": u.get("completion_tokens", 0),
                }
            continue

        delta = choices[0].get("delta", {})
        fr = choices[0].get("finish_reason")
        if fr is not None:
            finish_reason = fr

        # Send message_start on first real content
        if not sent_message_start:
            sent_message_start = True
            yield f'event: message_start\ndata: {json.dumps({"type":"message_start","message":{"id":message_id or "msg_","type":"message","role":"assistant","model":model,"content":[],"stop_reason":None,"usage":{"input_tokens":0,"output_tokens":0}}}, ensure_ascii=False)}\n\n'

        # Handle text content
        content = delta.get("content")
        if content:
            if not sent_text_block_start:
                sent_text_block_start = True
                yield f'event: content_block_start\ndata: {json.dumps({"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}, ensure_ascii=False)}\n\n'
            yield f'event: content_block_delta\ndata: {json.dumps({"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":content}}, ensure_ascii=False)}\n\n'
            text_buffer += content

        # Handle tool_calls (buffer for streaming)
        tool_calls_delta = delta.get("tool_calls")
        if tool_calls_delta:
            if not in_tool_call:
                in_tool_call = True
            for tcd in tool_calls_delta:
                idx = tcd.get("index", 0)
                while len(tool_call_buffer) <= idx:
                    tool_call_buffer.append({"id": "", "name": "", "arguments": ""})
                if tcd.get("id"):
                    tool_call_buffer[idx]["id"] = tcd["id"]
                func = tcd.get("function", {})
                if func.get("name"):
                    tool_call_buffer[idx]["name"] = func["name"]
                if func.get("arguments"):
                    tool_call_buffer[idx]["arguments"] += func["arguments"]

    # Close text block if opened
    if sent_text_block_start:
        yield f'event: content_block_stop\ndata: {json.dumps({"type":"content_block_stop","index":0}, ensure_ascii=False)}\n\n'

    # Emit buffered tool_use blocks
    for idx, tc in enumerate(tool_call_buffer):
        try:
            input_data = json.loads(tc["arguments"]) if tc["arguments"] else {}
        except json.JSONDecodeError:
            input_data = {}
        yield f'event: content_block_start\ndata: {json.dumps({"type":"content_block_start","index":(1 if sent_text_block_start else 0)+idx,"content_block":{"type":"tool_use","id":tc["id"],"name":tc["name"],"input":input_data}}, ensure_ascii=False)}\n\n'
        yield f'event: content_block_stop\ndata: {json.dumps({"type":"content_block_stop","index":(1 if sent_text_block_start else 0)+idx}, ensure_ascii=False)}\n\n'

    # Message delta with finish_reason and usage
    mapped_reason = _map_finish_reason(finish_reason)
    delta_payload: dict = {}
    if mapped_reason:
        delta_payload["stop_reason"] = mapped_reason
    delta_payload["stop_sequence"] = None

    message_delta = {"type": "message_delta", "delta": delta_payload}
    if usage_data:
        message_delta["usage"] = usage_data
    else:
        message_delta["usage"] = {"output_tokens": 0}

    yield f'event: message_delta\ndata: {json.dumps(message_delta, ensure_ascii=False)}\n\n'
    yield f'event: message_stop\ndata: {json.dumps({"type":"message_stop"}, ensure_ascii=False)}\n\n'
