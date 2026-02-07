"""
问答模块抽象基类

定义所有问答模块的统一接口规范
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from academic_agent.adapters import BaseAcademicAdapter
from academic_agent.exceptions import DataValidationError


class BaseQAModule(ABC):
    """
    所有问答模块的抽象基类
    
    该类定义了问答模块的标准接口，所有具体的问答模块（如基础查询、
    统计分析、关系分析等）都必须继承并实现这些抽象方法。
    
    Attributes:
        adapter: API适配器实例
        config: 模块配置字典
    
    Example:
        >>> class BasicQueryModule(BaseQAModule):
        ...     def handle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ...         # 实现查询逻辑
        ...         return {"code": 200, "data": {}, "msg": "success"}
    """
    
    def __init__(
        self, 
        adapter: BaseAcademicAdapter, 
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化问答模块
        
        Args:
            adapter: API适配器实例
            config: 模块配置（可选），包含模块特定的配置参数
        """
        self.adapter = adapter
        self.config = config or {}
    
    @abstractmethod
    def handle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理问答请求
        
        这是问答模块的核心方法，负责处理用户请求并返回标准化响应。
        
        Args:
            params: 请求参数字典，具体参数取决于模块类型
            
        Returns:
            标准化响应字典，格式为：
            {
                "code": 200,          # HTTP状态码
                "data": {...},        # 响应数据
                "msg": "success"      # 响应消息
            }
            
        Raises:
            DataValidationError: 参数验证失败时抛出
            APIRequestError: API请求失败时抛出
        """
        pass
    
    def validate_params(self, params: Dict[str, Any], required: List[str]) -> None:
        """
        验证必需参数
        
        检查参数字典中是否包含所有必需参数。
        
        Args:
            params: 参数字典
            required: 必需参数列表
            
        Raises:
            DataValidationError: 缺少必需参数时抛出
        """
        missing = [p for p in required if p not in params or params[p] is None]
        if missing:
            raise DataValidationError(
                f"缺少必需参数: {', '.join(missing)}"
            )
    
    def validate_year_range(
        self, 
        start_year: Optional[int], 
        end_year: Optional[int]
    ) -> None:
        """
        验证年份范围
        
        检查开始年份和结束年份是否有效。
        
        Args:
            start_year: 开始年份
            end_year: 结束年份
            
        Raises:
            DataValidationError: 年份范围无效时抛出
        """
        if start_year is not None and end_year is not None:
            if start_year > end_year:
                raise DataValidationError(
                    "开始年份不能大于结束年份",
                    field="year_range"
                )
    
    def success_response(self, data: Any, msg: str = "success") -> Dict[str, Any]:
        """
        构造成功响应
        
        Args:
            data: 响应数据
            msg: 响应消息
            
        Returns:
            标准化成功响应字典
        """
        return {
            "code": 200,
            "data": data,
            "msg": msg
        }
    
    def error_response(
        self, 
        code: int, 
        msg: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        构造错误响应
        
        Args:
            code: HTTP状态码
            msg: 错误消息
            details: 详细错误信息
            
        Returns:
            标准化错误响应字典
        """
        return {
            "code": code,
            "data": None,
            "msg": msg,
            "details": details or {}
        }
    
    @property
    @abstractmethod
    def module_name(self) -> str:
        """
        获取模块名称
        
        Returns:
            模块的唯一标识名称
        """
        pass
    
    @property
    @abstractmethod
    def module_description(self) -> str:
        """
        获取模块描述
        
        Returns:
            模块的功能描述
        """
        pass
