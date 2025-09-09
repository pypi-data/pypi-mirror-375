"""
测试上下文管理
"""

from src.runtime.context import PPIOAgentRuntimeContext
from src.runtime.models import RequestContext


class TestPPIOAgentRuntimeContext:
    """测试 PPIOAgentRuntimeContext 类"""

    def test_get_current_context_none(self):
        """测试获取当前上下文（无上下文）"""
        context = PPIOAgentRuntimeContext.get_current_context()
        assert context is None

    def test_set_and_get_current_context(self):
        """测试设置和获取当前上下文"""
        test_context = RequestContext(session_id="test-session")
        PPIOAgentRuntimeContext.set_current_context(test_context)

        context = PPIOAgentRuntimeContext.get_current_context()
        assert context == test_context
        assert context.session_id == "test-session"

    def test_clear_current_context(self):
        """测试清除当前上下文"""
        test_context = RequestContext(session_id="test-session")
        PPIOAgentRuntimeContext.set_current_context(test_context)

        # 确认上下文已设置
        assert PPIOAgentRuntimeContext.get_current_context() == test_context

        # 清除上下文
        PPIOAgentRuntimeContext.clear_current_context()

        # 确认上下文已清除
        assert PPIOAgentRuntimeContext.get_current_context() is None

    def test_create_context(self):
        """测试创建上下文"""
        context = PPIOAgentRuntimeContext.create_context()
        assert isinstance(context, RequestContext)
        assert context.session_id is None
        assert context.request_id is None
        assert context.headers == {}

    def test_create_context_with_values(self):
        """测试带值创建上下文"""
        context = PPIOAgentRuntimeContext.create_context(
            session_id="test-session",
            request_id="test-request",
            headers={"Authorization": "Bearer token"},
        )
        assert isinstance(context, RequestContext)
        assert context.session_id == "test-session"
        assert context.request_id == "test-request"
        assert context.headers == {"Authorization": "Bearer token"}
