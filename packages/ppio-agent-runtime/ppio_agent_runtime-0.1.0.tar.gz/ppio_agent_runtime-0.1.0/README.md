# PPIO Agent Runtime SDK

PPIO Agent Runtime SDK 是一个轻量级的 AI 智能体运行时框架，旨在为开发者提供简单易用的智能体部署解决方案。

## 核心特性

- **极简改造**：最小化代码修改，只需添加装饰器即可
- **零配置启动**：默认配置即可运行，无需复杂配置
- **容器化就绪**：专为 Docker 容器化部署设计
- **流式响应**：支持同步和异步流式输出
- **健康监控**：内置健康检查机制

## 快速开始

### 安装

```bash
pip install ppio-agent-runtime
```

### 基础使用

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

### 流式响应

```python
from ppio_agent_runtime import PPIOAgentRuntimeApp

app = PPIOAgentRuntimeApp()

@app.entrypoint
def streaming_agent(request: dict):
    """流式响应智能体"""
    query = request.get("query", "")
    
    for i in range(5):
        yield f"步骤 {i+1}: 处理 {query}"

if __name__ == "__main__":
    app.run()
```

### 异步智能体

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

## 部署

使用 PPIO CLI 工具部署你的智能体：

```bash
# 配置项目
ppio-agent configure

# 部署智能体
ppio-agent deploy
```

## 文档

- [API 参考](docs/api_reference.md)
- [部署指南](docs/deployment_guide.md)

## 许可证

MIT License
