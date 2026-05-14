from typing import Any, Literal

from pydantic import BaseModel, Field


# ---------- OpenAI ----------

class ChatMessage(BaseModel):
    role: str
    content: str | list[dict] | None = None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None
    name: str | None = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None
    tools: list[dict] | None = None
    tool_choice: Any = None
    response_format: Any = None
    stop: str | list[str] | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    user: str | None = None
    extra_body: dict | None = Field(default=None, exclude=True)


class Choice(BaseModel):
    index: int = 0
    message: ChatMessage | None = None
    delta: ChatMessage | None = None
    finish_reason: str | None = None


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[Choice]
    usage: Usage | None = None


class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: list[Choice]
    usage: Usage | None = None


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = 0
    owned_by: str = "ai-gateway"


class ModelsResponse(BaseModel):
    object: str = "list"
    data: list[ModelInfo]


# ---------- Anthropic ----------

class MessagesRequest(BaseModel):
    model: str
    messages: list[dict]
    system: str | list[dict] | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    stop_sequences: list[str] | None = None
    stream: bool = False
    tools: list[dict] | None = None
    tool_choice: Any = None
    thinking: Any = None


class ContentBlock(BaseModel):
    type: str
    text: str | None = None
    thinking: str | None = None
    signature: str | None = None
    id: str | None = None
    name: str | None = None
    input: dict | None = None
    content: Any = None


class MessagesResponse(BaseModel):
    id: str
    type: str = "message"
    role: str = "assistant"
    model: str
    content: list[ContentBlock]
    stop_reason: str | None = None
    stop_sequence: str | None = None
    usage: dict | None = None


class StreamEvent(BaseModel):
    type: str


class AnthropicErrorResponse(BaseModel):
    type: str = "error"
    error: dict
