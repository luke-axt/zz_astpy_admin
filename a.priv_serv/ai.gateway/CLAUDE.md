# AI Gateway 开发状态

## 当前进度

MVP 核心功能已全部实现，本地测试通过。

## 已实现功能

- [x] OpenAI API 转发：`POST /openai/v1/chat/completions`、`GET /openai/v1/models`
- [x] Claude Code 兼容：`POST /anthropic/v1/messages`（内部转换为 OpenAI ChatCompletions）
- [x] Streaming SSE（流式）支持：OpenAI 和 Anthropic 双向
- [x] Team API Key 认证：`Authorization: Bearer team_xxx`
- [x] 模型别名映射：通过 `config.yaml` 配置
- [x] SQLite 请求日志：`data/usage.sqlite`
- [x] 全局错误处理：不暴露上游 API Key

## 项目结构

```
ai.gateway/
├── app/
│   ├── main.py          # FastAPI 入口、lifespan 管理、全局异常处理
│   ├── config.py        # 配置加载（config.yaml + 环境变量）
│   ├── auth.py          # Team Key 校验 FastAPI dependency
│   ├── db.py            # SQLite 初始化 + 异步日志写入
│   ├── models.py        # Pydantic 请求/响应模型
│   ├── openai_client.py # httpx 调用真实 OpenAI API
│   ├── adapter.py       # Anthropic <=> OpenAI 协议转换（核心）
│   └── routers/
│       ├── openai.py    # /openai/v1/* 路由
│       └── anthropic.py # /anthropic/v1/messages 路由
├── config.yaml          # 模型映射 + Team Keys 配置
├── requirements.txt     # Python 依赖
└── .venv/               # 虚拟环境（已创建，未提交）
```

## 核心文件说明

### adapter.py
最关键的文件，负责 Anthropic Messages API 和 OpenAI ChatCompletions API 之间的双向转换：
- `anthropic_to_openai_request()`：将 Anthropic 请求转为 OpenAI 请求
- `openai_response_to_anthropic_response()`：将 OpenAI 响应转为 Anthropic 响应
- `openai_stream_to_anthropic_events()`：将 OpenAI SSE 流转为 Anthropic SSE 事件

### openai_client.py
使用 `httpx.AsyncClient` 复用连接池，统一处理：
- 网络超时（504）
- 网络错误（502）
- 上游异常（透传状态码）

### db.py
- `init_db()`：启动时自动建表（`data/usage.sqlite`）
- `log_request()`：异步写入，不记录 prompt 内容和敏感信息

## 环境变量需求

```bash
OPENAI_API_KEY=sk-...          # 必须
OPENAI_BASE_URL=https://...    # 可选，默认 https://api.openai.com/v1
PORT=8000                      # 可选
HOST=0.0.0.0                   # 可选
LOG_LEVEL=INFO                 # 可选
```

## 启动命令

```bash
cd ai.gateway
source .venv/Scripts/activate
set OPENAI_API_KEY=your-key
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 测试验证结果

| 场景 | 结果 |
|------|------|
| `GET /openai/v1/models` + 合法 Key | 200 OK，返回模型列表 |
| `GET /openai/v1/models` + 非法 Key | 401 Unauthorized |
| `POST /openai/v1/chat/completions` | 504 Gateway Timeout（中国网络环境预期行为） |
| `POST /anthropic/v1/messages` | 504 Gateway Timeout（同上） |
| SQLite 日志记录 | 正常，记录用户/端点/模型/状态码/耗时 |
| 工具调用协议转换 | Python 单元测试通过 |

## 已知问题 / 待完善

1. **上游网络**：当前未配置代理或中转，在中国网络环境下直接连接 OpenAI 会超时，需要配置 `OPENAI_BASE_URL` 指向可用中转地址
2. **Streaming token 统计**：流式场景下 prompt_tokens 统计依赖 `stream_options.include_usage`，部分上游可能不支持，目前统计为 0
3. **图片格式转换**：Anthropic 和 OpenAI 的图片 content block 格式略有差异，MVP 中未做深度转换
4. **限流**：第二阶段功能，当前未实现
5. **用量统计后台**：第二阶段功能，当前未实现

## 团队接入方式

### OpenAI SDK
```python
from openai import OpenAI
client = OpenAI(
    base_url="http://gateway:8000/openai/v1",
    api_key="team_eric_xxx"
)
```

### Claude Code
```bash
export ANTHROPIC_BASE_URL="http://gateway:8000/anthropic"
export ANTHROPIC_API_KEY="team_eric_xxx"
claude
```

## 下一步（验收后可继续）

- [ ] 配置真实可用的 `OPENAI_BASE_URL`
- [ ] 完整端到端测试（使用真实 OpenAI 上游）
- [ ] 第二阶段：限流、用量统计后台、多模型供应商
