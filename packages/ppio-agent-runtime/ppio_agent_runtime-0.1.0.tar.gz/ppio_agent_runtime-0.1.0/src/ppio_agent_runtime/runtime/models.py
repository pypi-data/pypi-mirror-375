"""
数据模型定义
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PingStatus(str, Enum):
    """健康状态枚举"""

    HEALTHY = "Healthy"
    HEALTHY_BUSY = "HealthyBusy"


class RequestContext(BaseModel):
    """简化的请求上下文"""

    session_id: Optional[str] = None
    request_id: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)

    class Config:
        extra = "allow"


class Response(BaseModel):
    """标准响应模型"""

    result: Any
    status: str = "success"
    message: Optional[str] = None

    class Config:
        extra = "allow"


class Error(BaseModel):
    """错误响应模型"""

    error: str
    error_type: str
    message: str

    class Config:
        extra = "allow"


class InvocationRequest(BaseModel):
    """调用请求模型"""

    prompt: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

    class Config:
        extra = "allow"


class PingResponse(BaseModel):
    """健康检查响应模型"""

    status: PingStatus
    message: Optional[str] = None
    timestamp: Optional[str] = None

    class Config:
        extra = "allow"
