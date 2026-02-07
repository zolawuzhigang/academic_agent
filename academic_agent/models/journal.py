"""
期刊数据模型模块

定义期刊相关的数据结构和转换方法
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Journal:
    """
    期刊数据模型类
    
    封装学术期刊的所有元数据信息，包括影响因子、出版商等。
    
    Attributes:
        journal_id: 期刊ID
        name: 期刊名称
        issn: ISSN号
        e_issn: 电子ISSN号
        publisher: 出版商
        impact_factor: 影响因子
        cite_score: CiteScore指标
        snip: SNIP指标
        sjr: SJR指标
        fields: 收录领域
        source: 数据来源API
    """
    
    name: str
    journal_id: Optional[str] = None
    issn: Optional[str] = None
    e_issn: Optional[str] = None
    publisher: Optional[str] = None
    impact_factor: Optional[float] = None
    cite_score: Optional[float] = None
    snip: Optional[float] = None
    sjr: Optional[float] = None
    fields: List[str] = field(default_factory=list)
    source: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将Journal对象转换为字典格式
        
        Returns:
            包含期刊所有属性的字典
        """
        return {
            "journal_id": self.journal_id,
            "name": self.name,
            "issn": self.issn,
            "e_issn": self.e_issn,
            "publisher": self.publisher,
            "impact_factor": self.impact_factor,
            "cite_score": self.cite_score,
            "snip": self.snip,
            "sjr": self.sjr,
            "fields": self.fields,
            "source": self.source
        }
    
    def get_impact_tier(self) -> str:
        """
        根据影响因子判断期刊等级
        
        Returns:
            期刊等级: "Q1", "Q2", "Q3", "Q4", "Unknown"
        """
        if self.impact_factor is None:
            return "Unknown"
        if self.impact_factor >= 10:
            return "Q1"
        elif self.impact_factor >= 5:
            return "Q2"
        elif self.impact_factor >= 2:
            return "Q3"
        else:
            return "Q4"
    
    def get_all_metrics(self) -> Dict[str, Optional[float]]:
        """
        获取所有期刊指标
        
        Returns:
            包含所有指标的字典
        """
        return {
            "impact_factor": self.impact_factor,
            "cite_score": self.cite_score,
            "snip": self.snip,
            "sjr": self.sjr
        }
    
    def __str__(self) -> str:
        """返回期刊的字符串表示"""
        if_str = f" IF:{self.impact_factor}" if self.impact_factor else ""
        return f"[{self.journal_id or 'N/A'}] {self.name}{if_str}"
