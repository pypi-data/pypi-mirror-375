"""
异步智能体示例
"""

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
