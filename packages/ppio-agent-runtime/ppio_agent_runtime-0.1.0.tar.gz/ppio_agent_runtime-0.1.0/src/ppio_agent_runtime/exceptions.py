"""
PPIO Agent Runtime SDK 异常定义
"""


class PPIOAgentRuntimeError(Exception):
    """PPIO Agent Runtime 基础异常类"""

    pass


class ValidationError(PPIOAgentRuntimeError):
    """验证错误"""

    pass


class RuntimeError(PPIOAgentRuntimeError):
    """运行时错误"""

    pass


class ConfigurationError(PPIOAgentRuntimeError):
    """配置错误"""

    pass


class HandlerError(PPIOAgentRuntimeError):
    """处理器错误"""

    pass
