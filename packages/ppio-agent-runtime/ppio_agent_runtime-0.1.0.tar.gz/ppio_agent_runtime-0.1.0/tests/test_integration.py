"""
集成测试
"""

import asyncio

from src.runtime.app import PPIOAgentRuntimeApp
from src.runtime.models import PingStatus


class TestIntegration:
    """集成测试"""

    def test_simple_sync_handler(self):
        """测试简单同步处理器"""
        app = PPIOAgentRuntimeApp()

        @app.entrypoint
        def simple_handler(request):
            return f"Hello {request.get('name', 'World')}"

        # 模拟请求数据
        request_data = {"name": "Test"}

        # 测试处理器调用
        result = simple_handler(request_data)
        assert result == "Hello Test"

    def test_simple_async_handler(self):
        """测试简单异步处理器"""
        app = PPIOAgentRuntimeApp()

        @app.entrypoint
        async def async_handler(request):
            await asyncio.sleep(0.01)  # 模拟异步操作
            return f"Async Hello {request.get('name', 'World')}"

        # 测试异步处理器调用
        async def test_async():
            request_data = {"name": "Test"}
            result = await async_handler(request_data)
            assert result == "Async Hello Test"

        asyncio.run(test_async())

    def test_streaming_handler(self):
        """测试流式处理器"""
        app = PPIOAgentRuntimeApp()

        @app.entrypoint
        def streaming_handler(request):
            name = request.get("name", "World")
            for i in range(3):
                yield f"Step {i + 1}: Hello {name}"

        # 测试流式处理器调用
        request_data = {"name": "Test"}
        results = list(streaming_handler(request_data))

        assert len(results) == 3
        assert results[0] == "Step 1: Hello Test"
        assert results[1] == "Step 2: Hello Test"
        assert results[2] == "Step 3: Hello Test"

    def test_async_streaming_handler(self):
        """测试异步流式处理器"""
        app = PPIOAgentRuntimeApp()

        @app.entrypoint
        async def async_streaming_handler(request):
            name = request.get("name", "World")
            for i in range(3):
                await asyncio.sleep(0.01)  # 模拟异步操作
                yield f"Async Step {i + 1}: Hello {name}"

        # 测试异步流式处理器调用
        async def test_async_streaming():
            request_data = {"name": "Test"}
            results = []
            async for result in async_streaming_handler(request_data):
                results.append(result)

            assert len(results) == 3
            assert results[0] == "Async Step 1: Hello Test"
            assert results[1] == "Async Step 2: Hello Test"
            assert results[2] == "Async Step 3: Hello Test"

        asyncio.run(test_async_streaming())

    def test_ping_handler(self):
        """测试健康检查处理器"""
        app = PPIOAgentRuntimeApp()

        @app.ping
        def custom_ping():
            return PingStatus.HEALTHY_BUSY

        # 测试健康检查处理器调用
        result = custom_ping()
        assert result == PingStatus.HEALTHY_BUSY

    def test_ping_handler_with_dict(self):
        """测试返回字典的健康检查处理器"""
        app = PPIOAgentRuntimeApp()

        @app.ping
        def custom_ping():
            return {"status": "Healthy", "message": "All good"}

        # 测试健康检查处理器调用
        result = custom_ping()
        assert result == {"status": "Healthy", "message": "All good"}

    def test_handler_with_context(self):
        """测试带上下文的处理器"""
        app = PPIOAgentRuntimeApp()

        @app.entrypoint
        def handler_with_context(request, context):
            return f"Session: {context.session_id}, Request: {request.get('data')}"

        # 模拟上下文
        from src.runtime.context import PPIOAgentRuntimeContext
        from src.runtime.models import RequestContext

        context = RequestContext(session_id="test-session")
        PPIOAgentRuntimeContext.set_current_context(context)

        try:
            # 测试处理器调用
            request_data = {"data": "test-data"}
            result = handler_with_context(request_data, context)
            assert result == "Session: test-session, Request: test-data"
        finally:
            PPIOAgentRuntimeContext.clear_current_context()

    def test_handler_without_context(self):
        """测试不带上下文的处理器"""
        app = PPIOAgentRuntimeApp()

        @app.entrypoint
        def handler_without_context(request):
            return f"Data: {request.get('data')}"

        # 测试处理器调用
        request_data = {"data": "test-data"}
        result = handler_without_context(request_data)
        assert result == "Data: test-data"
