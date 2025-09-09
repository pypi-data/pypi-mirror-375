"""
测试应用类
"""

from unittest.mock import patch

import pytest

from src.exceptions import HandlerError
from src.runtime.app import PPIOAgentRuntimeApp
from src.runtime.models import PingStatus, RequestContext


class TestPPIOAgentRuntimeApp:
    """测试 PPIOAgentRuntimeApp 类"""

    def test_init(self):
        """测试初始化"""
        app = PPIOAgentRuntimeApp()
        assert app.debug is False
        assert app._server is not None

        app_debug = PPIOAgentRuntimeApp(debug=True)
        assert app_debug.debug is True

    def test_entrypoint_decorator(self):
        """测试入口点装饰器"""
        app = PPIOAgentRuntimeApp()

        @app.entrypoint
        def my_handler(request):
            return "test"

        assert app._server.entrypoint_handler == my_handler

    def test_ping_decorator(self):
        """测试健康检查装饰器"""
        app = PPIOAgentRuntimeApp()

        @app.ping
        def my_ping():
            return PingStatus.HEALTHY

        assert app._server.ping_handler == my_ping

    def test_context_property(self):
        """测试上下文属性"""
        app = PPIOAgentRuntimeApp()

        # 没有设置上下文时应该返回 None
        assert app.context is None

        # 设置上下文后应该返回上下文
        context = RequestContext(session_id="test-session")
        with patch(
            "src.runtime.context.PPIOAgentRuntimeContext.get_current_context",
            return_value=context,
        ):
            assert app.context == context

    @patch("src.runtime.server.uvicorn.run")
    def test_run(self, mock_run):
        """测试运行方法"""
        app = PPIOAgentRuntimeApp()

        # 没有注册入口点处理器时应该抛出异常
        with pytest.raises(HandlerError):
            app.run()

        # 注册入口点处理器后应该能正常运行
        @app.entrypoint
        def my_handler(request):
            return "test"

        app.run(port=8080, host="127.0.0.1")

        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[1]["port"] == 8080
        assert call_args[1]["host"] == "127.0.0.1"
