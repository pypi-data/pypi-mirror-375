"""
简单智能体示例
"""

from src.runtime.app import PPIOAgentRuntimeApp

app = PPIOAgentRuntimeApp()


@app.entrypoint
def simple_agent(request: dict) -> str:
    """简单的智能体函数"""
    query = request.get("query", "")
    return f"处理查询: {query}"


if __name__ == "__main__":
    app.run()
