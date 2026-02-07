"""
作者数据模型模块

定义作者相关的数据结构和转换方法
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Author:
    """
    作者数据模型类
    
    封装学术作者的所有元数据信息，包括姓名、机构、学术指标等。
    
    Attributes:
        author_id: 统一作者ID
        name: 作者姓名
        affiliation: 所属机构
        email: 邮箱地址
        h_index: H指数
        citations: 总被引次数
        publications: 发文数量
        orcid: ORCID标识符
        fields: 研究领域
        source: 数据来源API
        raw_data: 原始数据（用于调试）
    """
    
    author_id: str
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    h_index: Optional[int] = None
    citations: Optional[int] = None
    publications: Optional[int] = None
    orcid: Optional[str] = None
    fields: List[str] = field(default_factory=list)
    source: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将Author对象转换为字典格式
        
        Returns:
            包含作者所有属性的字典
        """
        return {
            "author_id": self.author_id,
            "name": self.name,
            "affiliation": self.affiliation,
            "email": self.email,
            "h_index": self.h_index,
            "citations": self.citations,
            "publications": self.publications,
            "orcid": self.orcid,
            "fields": self.fields,
            "source": self.source
        }
    
    def get_full_name(self) -> str:
        """
        获取作者全名
        
        Returns:
            作者姓名
        """
        return self.name
    
    def get_affiliation_short(self, max_length: int = 50) -> str:
        """
        获取截断后的机构名称
        
        Args:
            max_length: 最大长度
            
        Returns:
            截断后的机构名称
        """
        if not self.affiliation:
            return "Unknown"
        if len(self.affiliation) <= max_length:
            return self.affiliation
        return self.affiliation[:max_length - 3] + "..."
    
    def __str__(self) -> str:
        """返回作者的字符串表示"""
        affil = f" ({self.affiliation})" if self.affiliation else ""
        return f"[{self.author_id}] {self.name}{affil}"
