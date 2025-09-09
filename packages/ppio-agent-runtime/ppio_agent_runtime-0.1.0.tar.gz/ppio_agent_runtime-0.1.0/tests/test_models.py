"""
测试数据模型
"""

from src.runtime.models import (
    Error,
    InvocationRequest,
    PingResponse,
    PingStatus,
    RequestContext,
    Response,
)


class TestPingStatus:
    """测试 PingStatus 枚举"""

    def test_values(self):
        """测试枚举值"""
        assert PingStatus.HEALTHY == "Healthy"
        assert PingStatus.HEALTHY_BUSY == "HealthyBusy"


class TestRequestContext:
    """测试 RequestContext 模型"""

    def test_init(self):
        """测试初始化"""
        context = RequestContext()
        assert context.session_id is None
        assert context.request_id is None
        assert context.headers == {}

    def test_init_with_values(self):
        """测试带值初始化"""
        context = RequestContext(
            session_id="test-session",
            request_id="test-request",
            headers={"Authorization": "Bearer token"},
        )
        assert context.session_id == "test-session"
        assert context.request_id == "test-request"
        assert context.headers == {"Authorization": "Bearer token"}

    def test_extra_fields(self):
        """测试额外字段"""
        context = RequestContext(session_id="test-session", custom_field="custom_value")
        assert context.custom_field == "custom_value"


class TestResponse:
    """测试 Response 模型"""

    def test_init(self):
        """测试初始化"""
        response = Response(result="test")
        assert response.result == "test"
        assert response.status == "success"
        assert response.message is None

    def test_init_with_all_fields(self):
        """测试带所有字段初始化"""
        response = Response(result="test", status="error", message="Test error")
        assert response.result == "test"
        assert response.status == "error"
        assert response.message == "Test error"


class TestError:
    """测试 Error 模型"""

    def test_init(self):
        """测试初始化"""
        error = Error(
            error="TestError",
            error_type="ValidationError",
            message="Test error message",
        )
        assert error.error == "TestError"
        assert error.error_type == "ValidationError"
        assert error.message == "Test error message"


class TestInvocationRequest:
    """测试 InvocationRequest 模型"""

    def test_init(self):
        """测试初始化"""
        request = InvocationRequest()
        assert request.prompt is None
        assert request.data is None
        assert request.session_id is None

    def test_init_with_values(self):
        """测试带值初始化"""
        request = InvocationRequest(
            prompt="Test prompt", data={"key": "value"}, session_id="test-session"
        )
        assert request.prompt == "Test prompt"
        assert request.data == {"key": "value"}
        assert request.session_id == "test-session"


class TestPingResponse:
    """测试 PingResponse 模型"""

    def test_init(self):
        """测试初始化"""
        response = PingResponse(status=PingStatus.HEALTHY)
        assert response.status == PingStatus.HEALTHY
        assert response.message is None
        assert response.timestamp is None

    def test_init_with_all_fields(self):
        """测试带所有字段初始化"""
        response = PingResponse(
            status=PingStatus.HEALTHY_BUSY,
            message="Processing",
            timestamp="2023-01-01T00:00:00Z",
        )
        assert response.status == PingStatus.HEALTHY_BUSY
        assert response.message == "Processing"
        assert response.timestamp == "2023-01-01T00:00:00Z"
