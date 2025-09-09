"""
上下文管理模块
"""

import contextvars
from typing import Dict, Optional

from .models import RequestContext


class PPIOAgentRuntimeContext:
    """运行时上下文管理器"""

    _current_context: contextvars.ContextVar[Optional[RequestContext]] = (
        contextvars.ContextVar("ppio_agent_runtime_context", default=None)
    )

    @classmethod
    def get_current_context(cls) -> Optional[RequestContext]:
        """获取当前请求上下文"""
        return cls._current_context.get()

    @classmethod
    def set_current_context(cls, context: RequestContext) -> None:
        """设置当前请求上下文"""
        cls._current_context.set(context)

    @classmethod
    def clear_current_context(cls) -> None:
        """清除当前请求上下文"""
        cls._current_context.set(None)

    @classmethod
    def create_context(
        cls,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> RequestContext:
        """创建新的请求上下文"""
        return RequestContext(
            session_id=session_id, request_id=request_id, headers=headers or {}
        )
