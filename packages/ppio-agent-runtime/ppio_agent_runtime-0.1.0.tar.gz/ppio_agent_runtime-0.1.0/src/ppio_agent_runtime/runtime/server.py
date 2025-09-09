"""
服务器启动和配置逻辑
"""

import inspect
import json
import logging
import os
import time
import uuid
from typing import Any, AsyncGenerator, Callable, Dict, Generator, Optional

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from ..exceptions import HandlerError, ValidationError
from .context import PPIOAgentRuntimeContext
from .models import InvocationRequest, PingResponse, PingStatus

logger = logging.getLogger(__name__)


class PPIOAgentRuntimeServer:
    """PPIO Agent Runtime 服务器"""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.entrypoint_handler: Optional[Callable] = None
        self.ping_handler: Optional[Callable] = None
        self.app: Optional[Starlette] = None

        # 配置日志
        self._setup_logging()

    def _setup_logging(self) -> None:
        """设置日志配置"""
        level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    def set_entrypoint_handler(self, handler: Callable) -> None:
        """设置入口点处理器"""
        self.entrypoint_handler = handler

    def set_ping_handler(self, handler: Callable) -> None:
        """设置健康检查处理器"""
        self.ping_handler = handler

    def _create_app(self) -> Starlette:
        """创建 Starlette 应用"""
        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ]

        routes = [
            Route("/invocations", self._handle_invocations, methods=["POST"]),
            Route("/ping", self._handle_ping, methods=["GET"]),
        ]

        return Starlette(routes=routes, middleware=middleware)

    async def _handle_invocations(self, request: Request) -> Any:
        """处理 /invocations 端点"""
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        try:
            # 解析请求
            payload = await request.json()
            invocation_request = InvocationRequest(**payload)
            logger.debug("Processing invocation request")

            # 创建请求上下文
            context = PPIOAgentRuntimeContext.create_context(
                session_id=invocation_request.session_id,
                request_id=request_id,
                headers=dict(request.headers),
            )

            # 设置当前上下文
            PPIOAgentRuntimeContext.set_current_context(context)

            try:
                if not self.entrypoint_handler:
                    logger.error("No entrypoint handler registered")
                    return JSONResponse({"error": "No entrypoint handler registered"}, status_code=500)

                # 调用处理器
                handler_name = self.entrypoint_handler.__name__ if hasattr(self.entrypoint_handler, "__name__") else "unknown"
                logger.debug("Invoking handler: %s", handler_name)

                result = await self._call_handler(
                    self.entrypoint_handler, invocation_request.dict(), context
                )

                duration = time.time() - start_time

                # 检查是否是生成器（流式响应）
                if inspect.isgenerator(result):
                    logger.info("Returning streaming response (generator) (%.3fs)", duration)
                    return StreamingResponse(
                        self._sync_stream_with_error_handling(result),
                        media_type="text/event-stream",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                        },
                    )
                elif inspect.isasyncgen(result):
                    logger.info("Returning streaming response (async generator) (%.3fs)", duration)
                    return StreamingResponse(
                        self._stream_with_error_handling(result),
                        media_type="text/event-stream",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                        },
                    )
                else:
                    # 同步响应
                    logger.info("Invocation completed successfully (%.3fs)", duration)
                    safe_json_string = self._safe_serialize_to_json_string(result)
                    return Response(safe_json_string, media_type="application/json")

            finally:
                # 清理上下文
                PPIOAgentRuntimeContext.clear_current_context()

        except json.JSONDecodeError as e:
            duration = time.time() - start_time
            logger.warning("Invalid JSON in request (%.3fs): %s", duration, e)
            return JSONResponse({"error": "Invalid JSON", "details": str(e)}, status_code=400)

        except ValidationError as e:
            duration = time.time() - start_time
            logger.error("Validation error (%.3fs): %s", duration, e)
            return JSONResponse({"error": "ValidationError", "details": str(e)}, status_code=400)

        except HandlerError as e:
            duration = time.time() - start_time
            logger.error("Handler error (%.3fs): %s", duration, e)
            return JSONResponse({"error": "HandlerError", "details": str(e)}, status_code=500)

        except Exception as e:
            duration = time.time() - start_time
            logger.exception("Invocation failed (%.3fs)", duration)
            return JSONResponse({"error": str(e)}, status_code=500)

    async def _handle_ping(self, request: Request) -> JSONResponse:
        """处理 /ping 端点"""
        try:
            if self.ping_handler:
                # 调用自定义健康检查
                result = await self._call_handler(self.ping_handler, {}, None)
                if isinstance(result, PingStatus):
                    status = result
                elif isinstance(result, dict) and "status" in result:
                    status = PingStatus(result["status"])
                else:
                    status = PingStatus.HEALTHY
            else:
                # 默认健康状态
                status = PingStatus.HEALTHY

            response = PingResponse(status=status)
            return JSONResponse(response.dict())

        except Exception as e:
            logger.error(f"Ping handler error: {e}")
            response = PingResponse(status=PingStatus.HEALTHY_BUSY, message=str(e))
            return JSONResponse(response.dict())

    async def _call_handler(
        self, handler: Callable, request_data: Dict[str, Any], context: Optional[Any]
    ) -> Any:
        """调用处理器函数"""
        import inspect

        # 检查函数签名
        sig = inspect.signature(handler)
        params = {}

        for param_name, _param in sig.parameters.items():
            if param_name == "request" or param_name == "data" or param_name == "payload":
                params[param_name] = request_data
            elif param_name == "context":
                if context is not None:
                    params[param_name] = context
            else:
                # 尝试从请求数据中获取参数
                if param_name in request_data:
                    params[param_name] = request_data[param_name]

        # 调用函数
        if inspect.iscoroutinefunction(handler):
            return await handler(**params)
        else:
            return handler(**params)

    def _safe_serialize_to_json_string(self, obj: Any) -> str:
        """安全地将对象序列化为 JSON 字符串"""
        try:
            # 尝试直接序列化
            return json.dumps(obj, ensure_ascii=False, default=str)
        except (TypeError, ValueError) as e:
            logger.warning("Failed to serialize object to JSON: %s", e)
            # 如果序列化失败，返回字符串表示
            return json.dumps({"result": str(obj)}, ensure_ascii=False)

    async def _stream_with_error_handling(self, async_generator: AsyncGenerator[Any, None]) -> AsyncGenerator[str, None]:
        """处理异步流式响应，带错误处理"""
        try:
            async for chunk in async_generator:
                # 安全序列化每个块
                safe_chunk = self._safe_serialize_to_json_string(chunk)
                yield f"data: {safe_chunk}\n\n"
        except Exception as e:
            logger.error("Async streaming error: %s", e)
            error_response = {"error": str(e), "error_type": "StreamingError"}
            yield f"data: {json.dumps(error_response)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    def _sync_stream_with_error_handling(self, generator: Generator[Any, None, None]) -> Generator[str, None, None]:
        """处理同步流式响应，带错误处理"""
        try:
            for chunk in generator:
                # 安全序列化每个块
                safe_chunk = self._safe_serialize_to_json_string(chunk)
                yield f"data: {safe_chunk}\n\n"
        except Exception as e:
            logger.error("Sync streaming error: %s", e)
            error_response = {"error": str(e), "error_type": "StreamingError"}
            yield f"data: {json.dumps(error_response)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    def run(self, port: int = 8080, host: Optional[str] = None) -> None:
        """启动服务器"""
        if not self.entrypoint_handler:
            raise HandlerError(
                "No entrypoint handler registered. Use @app.entrypoint decorator."
            )

        # 创建应用
        self.app = self._create_app()

        # 确定主机地址
        if host is None:
            host = "0.0.0.0" if os.getenv("CONTAINER") else "127.0.0.1"

        logger.info(f"Starting PPIO Agent Runtime server on {host}:{port}")

        # 启动服务器
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="debug" if self.debug else "info",
            access_log=self.debug,
        )
