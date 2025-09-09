"""
自定义健康检查智能体示例
"""

from ppio_agent_runtime import PingStatus, PPIOAgentRuntimeApp

app = PPIOAgentRuntimeApp()


@app.entrypoint
def my_agent(request: dict) -> str:
    """智能体函数"""
    return "Hello from agent"


@app.ping
def custom_health_check() -> PingStatus:
    """自定义健康检查"""
    # 可以检查数据库连接、外部服务等
    return PingStatus.HEALTHY


if __name__ == "__main__":
    app.run()
