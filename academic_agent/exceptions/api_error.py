"""
API异常模块

定义与API调用相关的异常类
"""

from typing import Dict, Any, Optional
from academic_agent.exceptions.base_error import AcademicAgentError


class APIError(AcademicAgentError):
    """
    API相关异常基类
    
    所有API异常的基类，用于处理与外部学术API交互时的错误。
    
    Example:
        >>> raise APIError("API调用失败", 500)
    """
    pass


class APIRequestError(APIError):
    """
    API请求异常
    
    当API请求失败时抛出，包含HTTP状态码信息。
    
    Attributes:
        status_code: HTTP响应状态码
    
    Example:
        >>> raise APIRequestError("请求超时", status_code=504)
    """
    
    def __init__(
        self, 
        message: str = "API请求失败", 
        status_code: Optional[int] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化API请求异常
        
        Args:
            message: 错误信息
            status_code: HTTP状态码
            details: 详细错误信息
        """
        self.status_code = status_code
        super().__init__(message, status_code or 500, details)


class RateLimitExceededError(APIError):
    """
    API频率限制异常
    
    当API请求频率超过限制时抛出，包含重试等待时间。
    
    Attributes:
        retry_after: 建议等待时间（秒）
    
    Example:
        >>> raise RateLimitExceededError(retry_after=60)
    """
    
    def __init__(
        self, 
        message: str = "API请求频率超限", 
        retry_after: int = 60, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化频率限制异常
        
        Args:
            message: 错误信息
            retry_after: 建议等待时间（秒）
            details: 详细错误信息
        """
        self.retry_after = retry_after
        super().__init__(message, 429, details)


class AuthenticationError(APIError):
    """
    API认证异常
    
    当API认证失败时抛出，通常由于API密钥无效或过期。
    
    Example:
        >>> raise AuthenticationError("API密钥无效")
    """
    
    def __init__(
        self, 
        message: str = "API认证失败", 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化认证异常
        
        Args:
            message: 错误信息
            details: 详细错误信息
        """
        super().__init__(message, 401, details)


class APINotAvailableError(APIError):
    """
    API不可用异常
    
    当API服务不可用时抛出，通常由于服务维护或网络问题。
    
    Example:
        >>> raise APINotAvailableError("OpenAlex服务暂时不可用")
    """
    
    def __init__(
        self, 
        message: str = "API服务不可用", 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化API不可用异常
        
        Args:
            message: 错误信息
            details: 详细错误信息
        """
        super().__init__(message, 503, details)
