# 部署指南

## 概述

本指南将介绍如何使用 PPIO CLI 工具部署使用 PPIO Agent Runtime SDK 开发的智能体。

## 前提条件

1. 安装 PPIO CLI 工具
2. 配置 E2B API Key
3. 确保 Control Plane 和 Data Plane 服务正在运行

## 快速开始

### 1. 创建智能体项目

```bash
mkdir my-agent
cd my-agent
```

### 2. 安装依赖

```bash
pip install ppio-agent-runtime
```

### 3. 创建智能体代码

创建 `app.py` 文件：

```python
from ppio_agent_runtime import PPIOAgentRuntimeApp

app = PPIOAgentRuntimeApp()

@app.entrypoint
def my_agent(request: dict) -> str:
    """我的智能体"""
    query = request.get("query", "")
    return f"处理查询: {query}"

if __name__ == "__main__":
    app.run()
```

### 4. 创建 requirements.txt

```txt
ppio-agent-runtime
```

### 5. 配置项目

```bash
ppio-agent configure
```

这将生成：
- `.ppio-agent.yaml` - 项目配置文件
- `e2b.Dockerfile` - E2B 沙箱配置
- `.dockerignore` - Docker 忽略文件

### 6. 部署智能体

```bash
ppio-agent deploy
```

## 项目结构

部署后的项目结构：

```
my-agent/
├── app.py                 # 智能体代码
├── requirements.txt       # Python 依赖
├── .ppio-agent.yaml      # PPIO 配置
├── e2b.Dockerfile        # E2B 沙箱配置
└── .dockerignore         # Docker 忽略文件
```

## 配置说明

### .ppio-agent.yaml

```yaml
default_agent: my-agent
agents:
  my-agent:
    name: my-agent
    description: "AI Agent deployed with PPIO Agent Runtime CLI"
    entrypoint: app.py
    platform: linux/arm64
    container_runtime: docker
    ppio:
      control_plane_url: "http://localhost:8000/v1"
      data_plane_url: "http://localhost:8001/v1"
      region: "us-east-1"
      network_configuration:
        network_mode: PUBLIC
      protocol_configuration:
        server_protocol: HTTP
    e2b:
      template_id: ""  # 部署后会自动填充
```

### e2b.Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建用户
RUN useradd -m -u 1000 ppio_agent

# 切换到非 root 用户
USER ppio_agent

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "app.py"]
```

## 环境变量

### 必需的环境变量

- `E2B_API_KEY`: E2B API 密钥

### 可选的环境变量

- `PPIO_API_KEY`: PPIO API 密钥（默认为 dev-api-key-123）
- `CONTAINER`: 设置为 "true" 表示在容器中运行

## 测试部署

### 1. 检查健康状态

```bash
curl http://localhost:8001/v1/health
```

### 2. 调用智能体

```bash
curl -X POST http://localhost:8001/v1/runtime/agent-{agentId}-production/invoke \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-123" \
  -d '{"query": "Hello World"}'
```

## 常见问题

### 1. 部署失败

**问题**: E2B 模板构建失败

**解决方案**:
- 检查 E2B_API_KEY 是否正确设置
- 确保网络连接正常
- 检查 Dockerfile 语法

### 2. 智能体无法启动

**问题**: 智能体容器启动失败

**解决方案**:
- 检查 app.py 中的代码语法
- 确保所有依赖都在 requirements.txt 中
- 检查端口配置（默认 8080）

### 3. 健康检查失败

**问题**: /ping 端点返回错误

**解决方案**:
- 检查自定义 ping 处理器的返回值
- 确保返回 PingStatus 枚举值或包含 status 字段的字典

## 高级配置

### 自定义端口

```python
if __name__ == "__main__":
    app.run(port=9000)
```

### 自定义主机

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

### 调试模式

```python
app = PPIOAgentRuntimeApp(debug=True)
```

## 监控和日志

### 查看日志

```bash
# 查看 Control Plane 日志
docker logs ppio-control-plane

# 查看 Data Plane 日志
docker logs ppio-data-plane
```

### 健康检查

```bash
# 检查 Control Plane
curl http://localhost:8000/v1/health

# 检查 Data Plane
curl http://localhost:8001/v1/health
```

## 最佳实践

1. **错误处理**: 在智能体函数中添加适当的错误处理
2. **日志记录**: 使用 Python 的 logging 模块记录重要信息
3. **资源管理**: 在长时间运行的任务中正确管理资源
4. **测试**: 在部署前充分测试智能体功能
5. **监控**: 设置适当的监控和告警
