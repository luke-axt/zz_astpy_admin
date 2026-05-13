# AI Gateway（团队内部 AI API 网关）需求文档

## 1. 项目背景

团队目前需要：

1. 在中国网络环境下稳定使用 OpenAI API
2. 支持 Claude Code 接入 OpenAI 模型
3. 为团队统一提供 AI API 服务入口
4. 避免向团队成员暴露真实 OpenAI API Key
5. 降低团队成员网络与配置复杂度
6. 后续可逐步扩展更多模型供应商

当前团队规模较小，不希望引入复杂的 AI 平台系统，因此决定采用：

> “轻量级 Python AI Gateway”

方案。

---

# 2. 项目目标

构建一个：

```text
内网可访问
轻量级
低维护成本
支持 OpenAI + Claude Code
```

的 AI API Gateway。

---

# 3. 系统定位

本系统不是：

* AI 管理平台
* SaaS 平台
* 多租户商业系统
* 复杂计费系统

而是：

> 团队内部 AI API 转换与统一入口服务。

---

# 4. 核心功能目标

系统需要实现：

| 功能             | 必须 |
| -------------- | -- |
| OpenAI API 转发  | 是  |
| Claude Code 支持 | 是  |
| OpenAI Key 隐藏  | 是  |
| 团队内部 Key 管理    | 是  |
| Streaming 支持   | 是  |
| 模型别名映射         | 是  |
| 请求日志           | 是  |
| 内网部署           | 是  |

---

# 5. 技术方案

## 5.1 技术栈

### 服务端

```text
Python 3.11+
FastAPI
httpx
uvicorn
```

### 数据存储

初期：

```text
SQLite
```

### 部署方式

```text
python+window原生运行
```

---

# 6. 系统架构

## 6.1 总体架构

```text
团队成员
    │
    ├── Claude Code
    │        │
    │        ▼
    │   /anthropic/v1/messages
    │
    └── OpenAI SDK / 应用
             │
             ▼
        /openai/v1/*
             │
             ▼
      AI Gateway（本系统）
             │
             ▼
          OpenAI API
```

---

# 7. 功能需求

# 7.1 OpenAI Compatible API

系统需要兼容 OpenAI API 格式。

## 支持接口

### 必须支持

```text
/openai/v1/chat/completions
/openai/v1/responses
/openai/v1/models
```

### 可选支持

```text
/openai/v1/embeddings
```

---

## 行为要求

### 请求

客户端：

```text
OpenAI SDK
Cursor
Cline
自定义程序
```

仅需修改：

```text
base_url
api_key
```

即可接入。

---

### 响应

响应格式需尽量保持 OpenAI 原始格式。

---

### Streaming

必须支持：

```text
stream=true
```

并保持 SSE 转发能力。

---

# 7.2 Claude Code Compatible API

系统需支持 Claude Code 接入。

---

## 支持接口

### 必须支持

```text
/anthropic/v1/messages
```

---

## 行为要求

### 请求协议

接收：

```text
Anthropic Messages API
```

格式请求。

---

### 内部转换

系统需将 Anthropic Messages 请求：

```text
messages
system
tools
stream
```

转换为：

```text
OpenAI Responses API
或 ChatCompletions API
```

---

### 响应协议

返回：

```text
Anthropic-compatible response
```

供 Claude Code 正常工作。

---

### Streaming

必须支持：

```text
Anthropic stream events
```

---

# 7.3 模型映射系统

系统需支持内部模型别名。

---

## 示例

```text
code-fast   -> gpt-4.1-mini
code-strong -> gpt-4.1
reasoning   -> o3
```

---

## 目标

避免团队成员直接依赖真实模型名称。

方便后期统一替换模型。

---

# 7.4 Team API Key 管理

系统需支持内部 Team Key。

---

## 示例

```text
team_eric_xxx
team_dev_xxx
```

---

## 行为要求

### 校验

所有请求必须：

```text
Authorization: Bearer team_xxx
```

---

### 服务端

服务端内部：

```text
使用真实 OpenAI API Key
```

客户端永远不可见。

---

# 7.5 日志系统

系统需记录：

| 字段        | 必须 |
| --------- | -- |
| 时间        | 是  |
| 用户        | 是  |
| endpoint  | 是  |
| 模型        | 是  |
| 请求状态      | 是  |
| token 使用量 | 是  |
| 请求耗时      | 是  |

---

## 安全要求

禁止记录：

* 完整 prompt
* OpenAI API Key
* 敏感 header

---

# 7.6 错误处理

系统需统一处理：

* OpenAI 网络错误
* 超时
* rate limit
* 无效请求
* 未授权
* 上游异常

并返回兼容格式错误。

---

# 8. 非功能需求

# 8.1 部署要求

系统需：

```text
独立部署
不依赖 Java 环境
```

---

# 8.2 网络要求

系统仅需：

```text
内网访问
```

无需公网暴露。

---

# 8.3 性能要求

初期支持：

```text
5~20 人团队
```

即可。

---

# 8.4 可维护性

系统需：

* 代码结构简单
* 低依赖
* 低学习成本
* 可单人维护

---

# 9. 配置方案

## 9.1 环境变量

### OpenAI

```text
OPENAI_API_KEY=
OPENAI_BASE_URL=
```

---

### 服务配置

```text
PORT=
HOST=
LOG_LEVEL=
```

---

# 9.2 模型配置

建议使用：

```yaml
models:
  code-fast: gpt-4.1-mini
  code-strong: gpt-4.1
  reasoning: o3
```

---

# 9.3 Team Key 配置

建议：

```yaml
team_keys:
  team_eric_xxx:
    user: eric
  team_dev_xxx:
    user: dev
```

---

# 10. 推荐项目结构

```text
ai-gateway/
├── app/
│   ├── api/
│   ├── providers/
│   ├── adapters/
│   ├── auth/
│   ├── models/
│   ├── logging/
│   └── config/
│
├── data/
│   └── usage.sqlite
│
├── config.yaml
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

# 11. 第一阶段（MVP）

## 必须完成

### OpenAI 转发

```text
/openai/v1/chat/completions
```

---

### Claude Code 支持

```text
/anthropic/v1/messages
```

---

### Streaming

必须支持。

---

### Team API Key

必须支持。


---

# 12. 第二阶段（后续）

## 可选功能

### 用量统计

按：

* 用户
* 模型
* 日期

统计。

---

### 限流

限制：

* 每分钟请求数
* 并发数

---

### 多模型供应商

未来支持：

* Gemini
* DeepSeek
* Azure OpenAI

---

### 管理后台

后期再考虑。

---

# 13. 不做的功能（明确范围）

当前版本不做：

* 用户注册系统
* 支付系统
* SaaS 多租户
* 复杂 RBAC
* Kubernetes
* Redis 集群
* 高可用架构
* 多区域部署
* Web 管理后台

---

# 14. 最终目标

最终形成：

```text
团队统一 AI API 入口
```

实现：

* 稳定访问 OpenAI
* Claude Code 可用
* 团队统一配置
* 统一安全控制
* 低维护成本
* 可逐步扩展模型供应商

---

# 15. 成功标准

以下场景视为成功：

## Claude Code

团队成员可直接：

```text
配置 ANTHROPIC_BASE_URL
```

正常使用 Claude Code。

---

## OpenAI SDK

团队成员：

```python
base_url -> AI Gateway
```

即可正常调用。

---

## 安全

团队成员无法获取真实 OpenAI Key。

---

## 运维

系统可由单人维护。
