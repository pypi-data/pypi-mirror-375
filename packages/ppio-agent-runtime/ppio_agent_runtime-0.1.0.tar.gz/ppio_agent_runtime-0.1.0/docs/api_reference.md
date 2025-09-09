# API 参考

## PPIOAgentRuntimeApp

PPIO Agent Runtime 的核心应用类。

### 构造函数

```python
PPIOAgentRuntimeApp(debug: bool = False)
```

**参数:**
- `debug` (bool): 启用调试模式，默认为 False

### 方法

#### entrypoint

```python
@app.entrypoint
def my_handler(request: dict) -> Any:
    """主入口点函数"""
    pass
```

注册主入口点函数。这个函数将处理所有的 `/invocations` 请求。

**参数:**
- `request` (dict): 请求数据，包含 `prompt`、`data`、`session_id` 等字段

**返回值:**
- 可以是任何可序列化的对象，或者生成器（用于流式响应）

#### ping

```python
@app.ping
def my_ping() -> PingStatus:
    """自定义健康检查函数"""
    pass
```

注册自定义健康检查函数（可选）。这个函数将处理 `/ping` 请求。

**返回值:**
- `PingStatus`: 健康状态枚举值
- `dict`: 包含 `status` 字段的字典

#### run

```python
app.run(port: int = 8080, host: Optional[str] = None)
```

启动服务器。

**参数:**
- `port` (int): 端口号，默认为 8080
- `host` (Optional[str]): 主机地址，默认为自动检测

### 属性

#### context

```python
context: Optional[RequestContext]
```

获取当前请求上下文。

## RequestContext

请求上下文类，包含当前请求的元数据。

### 属性

- `session_id` (Optional[str]): 会话 ID
- `request_id` (Optional[str]): 请求 ID
- `headers` (Dict[str, str]): 请求头

## PingStatus

健康状态枚举。

### 值

- `HEALTHY`: 健康状态
- `HEALTHY_BUSY`: 健康但忙碌状态

## 异常

### PPIOAgentRuntimeError

基础异常类。

### ValidationError

验证错误。

### RuntimeError

运行时错误。

### ConfigurationError

配置错误。

### HandlerError

处理器错误。

## 使用示例

### 基础使用

```python
from ppio_agent_runtime import PPIOAgentRuntimeApp

app = PPIOAgentRuntimeApp()

@app.entrypoint
def my_agent(request: dict) -> str:
    query = request.get("query", "")
    return f"处理查询: {query}"

if __name__ == "__main__":
    app.run()
```

### 流式响应

```python
@app.entrypoint
def streaming_agent(request: dict):
    query = request.get("query", "")
    for i in range(5):
        yield f"步骤 {i+1}: 处理 {query}"
```

### 异步处理

```python
import asyncio

@app.entrypoint
async def async_agent(request: dict) -> str:
    query = request.get("query", "")
    await asyncio.sleep(1)
    return f"异步处理完成: {query}"
```

### 带上下文

```python
from ppio_agent_runtime import RequestContext

@app.entrypoint
def context_agent(request: dict, context: RequestContext) -> str:
    query = request.get("query", "")
    session_id = context.session_id or "unknown"
    return f"会话 {session_id}: 处理查询 {query}"
```

### 自定义健康检查

```python
from ppio_agent_runtime import PingStatus

@app.ping
def custom_health_check() -> PingStatus:
    # 检查数据库连接、外部服务等
    return PingStatus.HEALTHY
```
