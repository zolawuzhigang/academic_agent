"""
数据处理异常模块

定义与数据处理相关的异常类
"""

from typing import Dict, Any, Optional
from academic_agent.exceptions.base_error import AcademicAgentError


class DataError(AcademicAgentError):
    """
    数据处理异常基类
    
    所有数据异常的基类，用于处理数据验证、转换等操作时的错误。
    
    Example:
        >>> raise DataError("数据处理失败", 500)
    """
    pass


class PaperNotFoundError(DataError):
    """
    论文不存在异常
    
    当根据ID查询不到论文时抛出。
    
    Attributes:
        paper_id: 查询的论文ID
    
    Example:
        >>> raise PaperNotFoundError("W1234567890")
    """
    
    def __init__(self, paper_id: str, message: Optional[str] = None):
        """
        初始化论文不存在异常
        
        Args:
            paper_id: 论文ID
            message: 自定义错误信息，默认使用paper_id生成
        """
        self.paper_id = paper_id
        msg = message or f"论文不存在: {paper_id}"
        super().__init__(msg, 404)


class AuthorNotFoundError(DataError):
    """
    作者不存在异常
    
    当根据ID查询不到作者时抛出。
    
    Attributes:
        author_id: 查询的作者ID
    
    Example:
        >>> raise AuthorNotFoundError("A1234567890")
    """
    
    def __init__(self, author_id: str, message: Optional[str] = None):
        """
        初始化作者不存在异常
        
        Args:
            author_id: 作者ID
            message: 自定义错误信息，默认使用author_id生成
        """
        self.author_id = author_id
        msg = message or f"作者不存在: {author_id}"
        super().__init__(msg, 404)


class JournalNotFoundError(DataError):
    """
    期刊不存在异常
    
    当根据ID查询不到期刊时抛出。
    
    Attributes:
        journal_id: 查询的期刊ID
    
    Example:
        >>> raise JournalNotFoundError("J1234567890")
    """
    
    def __init__(self, journal_id: str, message: Optional[str] = None):
        """
        初始化期刊不存在异常
        
        Args:
            journal_id: 期刊ID
            message: 自定义错误信息，默认使用journal_id生成
        """
        self.journal_id = journal_id
        msg = message or f"期刊不存在: {journal_id}"
        super().__init__(msg, 404)


class DataValidationError(DataError):
    """
    数据验证异常
    
    当数据验证失败时抛出，包含字段信息。
    
    Attributes:
        field: 验证失败的字段名
    
    Example:
        >>> raise DataValidationError("年份格式错误", field="publish_year")
    """
    
    def __init__(
        self, 
        message: str = "数据验证失败", 
        field: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化数据验证异常
        
        Args:
            message: 错误信息
            field: 验证失败的字段名
            details: 详细错误信息
        """
        self.field = field
        super().__init__(message, 400, details)


class DataConversionError(DataError):
    """
    数据转换异常
    
    当数据格式转换失败时抛出，包含源格式和目标格式信息。
    
    Attributes:
        source_format: 源数据格式
        target_format: 目标数据格式
    
    Example:
        >>> raise DataConversionError("XML解析失败", "xml", "json")
    """
    
    def __init__(
        self, 
        message: str = "数据转换失败", 
        source_format: Optional[str] = None, 
        target_format: Optional[str] = None
    ):
        """
        初始化数据转换异常
        
        Args:
            message: 错误信息
            source_format: 源数据格式
            target_format: 目标数据格式
        """
        self.source_format = source_format
        self.target_format = target_format
        super().__init__(message, 500)
