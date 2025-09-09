"""
流式响应智能体示例
"""

from ppio_agent_runtime import PPIOAgentRuntimeApp

app = PPIOAgentRuntimeApp()


@app.entrypoint
def streaming_agent(request: dict):
    """流式响应智能体"""
    query = request.get("query", "")

    # 同步生成器
    for i in range(5):
        yield f"步骤 {i + 1}: 处理 {query}"


if __name__ == "__main__":
    app.run()
