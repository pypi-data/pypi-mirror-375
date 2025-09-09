# PPIO Agent Runtime SDK 设计文档

## 1. 项目概述

### 1.1 项目定位

PPIO Agent Runtime SDK 是一个轻量级的 AI 智能体运行时框架，旨在为开发者提供简单易用的智能体部署解决方案。该 SDK 专注于核心运行时功能，去除复杂的任务管理和云平台特定功能，让开发者能够快速将现有的 AI 智能体代码改造并部署到容器化环境中。

### 1.2 核心价值主张

- **极简改造**：最小化代码修改，只需添加装饰器即可
- **零配置启动**：默认配置即可运行，无需复杂配置
- **容器化就绪**：专为 Docker 容器化部署设计
- **流式响应**：支持同步和异步流式输出
- **健康监控**：内置健康检查机制

### 1.3 目标用户

1. **AI 应用开发者**：希望快速部署 AI 智能体的开发者
2. **原型开发者**：需要快速验证 AI 应用概念的开发者
3. **容器化团队**：专注于容器化部署的开发团队
4. **微服务架构**：需要轻量级 AI 服务的团队

## 2. 总体架构设计

### 2.1 架构层次图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户 Agent 代码                          │
├─────────────────────────────────────────────────────────────────┤
│                    PPIO Agent Runtime SDK                    │
│  ┌─────────────────┬─────────────────┬─────────────────────────┐  │
│  │   Runtime       │    Context      │       Models            │  │
│  │   ├─ app.py     │   ├─ context.py │     ├─ models.py        │  │
│  │   └─ server.py  │   └─ ...        │     └─ ...              │  │
│  └─────────────────┴─────────────────┴─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                      HTTP 服务器层                              │
│  ┌─────────────────┬─────────────────┬─────────────────────────┐  │
│  │   Starlette     │    Uvicorn      │    ASGI 接口            │  │
│  │   Web 框架      │   ASGI 服务器   │   ├─ 请求处理            │  │
│  │                 │                 │   ├─ 响应生成            │  │
│  │                 │                 │   └─ 错误处理            │  │
│  └─────────────────┴─────────────────┴─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心模块关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                    PPIOAgentRuntimeApp                        │
│                      (核心应用框架)                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Context  │ │ Models   │ │ Server   │
│ Manager  │ │ Manager  │ │ Manager  │
└──────────┘ └──────────┘ └──────────┘
      │           │           │
      ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Request  │ │ Status   │ │ HTTP     │
│ Context  │ │ Models   │ │ Handler  │
└──────────┘ └──────────┘ └──────────┘
```

## 3. 模块详细设计

### 3.1 Runtime 模块 (核心运行时)

**位置**: `src/runtime/`

**主要文件**:
- `app.py`: 核心应用类 PPIOAgentRuntimeApp
- `server.py`: 服务器启动和配置逻辑
- `context.py`: 请求上下文管理
- `models.py`: 数据模型定义

**功能特性**:

1. **Web 服务框架**
   - 基于 Starlette 构建的轻量级异步 Web 框架
   - 支持 HTTP 端点：`/invocations` (POST) 和 `/ping` (GET)
   - 自动处理同步/异步函数调用

2. **装饰器系统**
   - `@app.entrypoint`: 注册主入口点函数
   - `@app.ping`: 自定义健康检查状态（可选）

3. **健康状态管理**
   - 自动检测：HEALTHY / HEALTHY_BUSY
   - 简化的状态管理，无复杂任务跟踪

4. **流式响应支持**
   - 支持同步和异步生成器
   - Server-Sent Events (SSE) 格式输出
   - 错误处理和安全序列化

**架构特点**:
- 线程安全的请求处理
- 上下文变量传递
- 自动错误处理和日志记录
- 无状态设计，适合容器化部署

### 3.2 Context 模块 (上下文管理)

**位置**: `src/context.py`

**功能特性**:

1. **请求上下文**
   - 会话 ID 管理
   - 请求元数据提取
   - 简化的头部处理

2. **上下文传递**
   - 线程安全的上下文变量
   - 自动上下文清理
   - 可选的上下文注入

**设计原则**:
- 最小化依赖
- 线程安全
- 易于扩展

### 3.3 Models 模块 (数据模型)

**位置**: `src/models.py`

**功能特性**:

1. **状态模型**
   - `PingStatus`: 健康状态枚举
   - 简化的状态定义

2. **请求/响应模型**
   - 基础请求结构
   - 标准响应格式
   - 错误模型定义

3. **配置模型**
   - 应用配置
   - 服务器配置
   - 日志配置

## 4. 核心 API 设计

### 4.1 应用类 API

```python
class PPIOAgentRuntimeApp:
    """PPIO Agent Runtime 应用类"""
    
    def __init__(self, debug: bool = False):
        """初始化应用
        
        Args:
            debug: 启用调试模式
        """
        pass
    
    def entrypoint(self, func: Callable) -> Callable:
        """注册主入口点函数
        
        Args:
            func: 要注册的函数
            
        Returns:
            装饰后的函数
        """
        pass
    
    def ping(self, func: Callable) -> Callable:
        """注册自定义健康检查函数（可选）
        
        Args:
            func: 健康检查函数
            
        Returns:
            装饰后的函数
        """
        pass
    
    def run(self, port: int = 8080, host: Optional[str] = None):
        """启动服务器
        
        Args:
            port: 端口号，默认 8080
            host: 主机地址，默认自动检测
        """
        pass
```

### 4.2 上下文 API

```python
class RequestContext:
    """简化的请求上下文"""
    
    session_id: Optional[str] = None
    
    def __init__(self, session_id: Optional[str] = None):
        """初始化请求上下文
        
        Args:
            session_id: 会话 ID
        """
        pass

class PPIOAgentRuntimeContext:
    """运行时上下文管理器"""
    
    @classmethod
    def get_current_context(cls) -> Optional[PPIORequestContext]:
        """获取当前请求上下文"""
        pass
```

### 4.3 模型 API

```python
class PingStatus(str, Enum):
    """健康状态枚举"""
    HEALTHY = "Healthy"
    HEALTHY_BUSY = "HealthyBusy"

class Response(BaseModel):
    """标准响应模型"""
    result: Any
    status: str = "success"
    message: Optional[str] = None

class Error(BaseModel):
    """错误响应模型"""
    error: str
    error_type: str
    message: str
```

## 5. 使用示例

### 5.1 基础使用

```python
from ppio_agent_runtime import PPIOAgentRuntimeApp

app = PPIOAgentRuntimeApp()

@app.entrypoint
def my_agent(request: dict) -> str:
    """简单的智能体函数"""
    query = request.get("query", "")
    return f"处理查询: {query}"

if __name__ == "__main__":
    app.run()
```

### 5.2 带上下文的智能体

```python
from ppio_agent_runtime import PPIOAgentRuntimeApp, RequestContext

app = PPIOAgentRuntimeApp()

@app.entrypoint
def my_agent(request: dict, context: RequestContext) -> str:
    """带上下文的智能体函数"""
    query = request.get("query", "")
    session_id = context.session_id or "unknown"
    return f"会话 {session_id}: 处理查询 {query}"

if __name__ == "__main__":
    app.run()
```

### 5.3 流式响应智能体

```python
from ppio_agent_runtime import PPIOAgentRuntimeApp

app = PPIOAgentRuntimeApp()

@app.entrypoint
def streaming_agent(request: dict):
    """流式响应智能体"""
    query = request.get("query", "")
    
    # 同步生成器
    for i in range(5):
        yield f"步骤 {i+1}: 处理 {query}"

if __name__ == "__main__":
    app.run()
```

### 5.4 异步智能体

```python
import asyncio
from ppio_agent_runtime import PPIOAgentRuntimeApp

app = PPIOAgentRuntimeApp()

@app.entrypoint
async def async_agent(request: dict) -> str:
    """异步智能体函数"""
    query = request.get("query", "")
    
    # 模拟异步处理
    await asyncio.sleep(1)
    return f"异步处理完成: {query}"

if __name__ == "__main__":
    app.run()
```

### 5.5 自定义健康检查

```python
from ppio_agent_runtime import PPIOAgentRuntimeApp, PingStatus

app = PPIOAgentRuntimeApp()

@app.entrypoint
def my_agent(request: dict) -> str:
    return "Hello from agent"

@app.ping
def custom_health_check() -> PingStatus:
    """自定义健康检查"""
    # 可以检查数据库连接、外部服务等
    return PingStatus.HEALTHY

if __name__ == "__main__":
    app.run()
```

## 6. 技术特性

### 6.1 设计原则

1. **简单优先**: 最小化 API 复杂度
2. **零配置**: 默认配置即可运行
3. **容器友好**: 专为容器化设计
4. **类型安全**: 完整的类型注解支持
5. **异步支持**: 原生 async/await 支持

### 6.2 性能特性

1. **轻量级**: 最小化依赖和内存占用
2. **高性能**: 基于 Starlette 的高性能 Web 框架
3. **并发处理**: 支持高并发请求处理
4. **流式处理**: 支持大响应流的处理

### 6.3 可扩展性

1. **插件化**: 支持自定义中间件
2. **配置驱动**: 灵活的配置管理
3. **模块化**: 清晰的模块分离
4. **版本兼容**: 向后兼容的 API 设计

## 7. 部署特性

### 7.1 容器化支持

- **Docker 就绪**: 专为 Docker 容器设计
- **环境检测**: 自动检测容器环境
- **端口配置**: 灵活的端口和主机配置
- **健康检查**: 内置健康检查端点

### 7.2 生产就绪

- **错误处理**: 完善的错误处理机制
- **日志记录**: 结构化日志输出
- **监控支持**: 支持 Prometheus 等监控系统
- **优雅关闭**: 支持优雅关闭和资源清理

## 8. 项目结构

```
ppio-agent-runtime-sdk/
├── pyproject.toml
├── README.md
├── src/
│   ├── __init__.py
│   ├── runtime/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── server.py
│   │   ├── context.py
│   │   └── models.py
│   └── exceptions.py
├── tests/
│   ├── test_app.py
│   ├── test_context.py
│   ├── test_models.py
│   └── test_integration.py
└── docs/
    ├── api_reference.md
    └── deployment_guide.md
```

## 9. 依赖管理

### 9.1 核心依赖

```toml
dependencies = [
    "starlette>=0.46.2",
    "uvicorn>=0.34.2",
    "pydantic>=2.0.0,<3.0.0",
    "typing-extensions>=4.13.2,<5.0.0",
]
```

### 9.2 开发依赖

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.4.1",
    "pytest-asyncio>=0.24.0",
    "mypy>=1.16.1",
    "ruff>=0.12.0",
    "httpx>=0.28.1",
]
```

## 10. 总结

PPIO Agent Runtime SDK 是一个专注于核心运行时功能的轻量级框架，为开发者提供了简单易用的智能体部署解决方案。通过最小化的 API 设计和容器化的部署特性，开发者可以快速将现有的 AI 智能体代码改造并部署到生产环境中。

**主要优势**:
1. 极简的 API 设计
2. 零配置启动
3. 容器化就绪
4. 完整的异步支持
5. 流式响应支持

**适用场景**:
1. 快速原型开发
2. 微服务架构
3. 容器化部署
4. 轻量级 AI 服务
5. 教学和演示项目

该 SDK 为 AI 应用开发提供了简单而强大的运行时基础，让开发者能够专注于业务逻辑而非基础设施管理。
