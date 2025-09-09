"""
带上下文的智能体示例
"""

from ppio_agent_runtime import PPIOAgentRuntimeApp, RequestContext

app = PPIOAgentRuntimeApp()


@app.entrypoint
def context_agent(request: dict, context: RequestContext) -> str:
    """带上下文的智能体函数"""
    query = request.get("query", "")
    session_id = context.session_id or "unknown"
    return f"会话 {session_id}: 处理查询 {query}"


if __name__ == "__main__":
    app.run()
