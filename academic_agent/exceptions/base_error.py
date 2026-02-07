"""
基础异常模块

定义学术Agent的基础异常类
"""

from typing import Dict, Any, Optional


class AcademicAgentError(Exception):
    """
    学术Agent基础异常类
    
    所有自定义异常的基类，提供统一的错误处理接口。
    
    Attributes:
        message: 错误信息
        code: HTTP状态码
        details: 详细错误信息字典
    
    Example:
        >>> raise AcademicAgentError("操作失败", 500, {"reason": "timeout"})
    """
    
    def __init__(
        self, 
        message: str, 
        code: int = 500, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化异常
        
        Args:
            message: 错误信息
            code: HTTP状态码，默认为500
            details: 详细错误信息，默认为空字典
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将异常转换为字典格式
        
        Returns:
            包含异常信息的字典
        """
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": self.details
        }
    
    def __str__(self) -> str:
        """返回异常的字符串表示"""
        return f"[{self.code}] {self.message}"
