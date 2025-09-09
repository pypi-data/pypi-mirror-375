"""
核心应用类
"""

from typing import Callable, Optional

from .context import PPIOAgentRuntimeContext
from .models import RequestContext
from .server import PPIOAgentRuntimeServer


class PPIOAgentRuntimeApp:
    """PPIO Agent Runtime 应用类"""

    def __init__(self, debug: bool = False):
        """初始化应用

        Args:
            debug: 启用调试模式
        """
        self.debug = debug
        self._server = PPIOAgentRuntimeServer(debug=debug)

    def entrypoint(self, func: Callable) -> Callable:
        """注册主入口点函数

        Args:
            func: 要注册的函数

        Returns:
            装饰后的函数
        """
        self._server.set_entrypoint_handler(func)
        return func

    def ping(self, func: Callable) -> Callable:
        """注册自定义健康检查函数（可选）

        Args:
            func: 健康检查函数

        Returns:
            装饰后的函数
        """
        self._server.set_ping_handler(func)
        return func

    def run(self, port: int = 8080, host: Optional[str] = None) -> None:
        """启动服务器

        Args:
            port: 端口号，默认 8080
            host: 主机地址，默认自动检测
        """
        self._server.run(port=port, host=host)

    @property
    def context(self) -> Optional[RequestContext]:
        """获取当前请求上下文"""
        return PPIOAgentRuntimeContext.get_current_context()
