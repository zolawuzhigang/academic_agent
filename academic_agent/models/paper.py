"""
论文数据模型模块

定义论文相关的数据结构和转换方法
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Paper:
    """
    论文数据模型类
    
    封装学术论文的所有元数据信息，包括标题、作者、期刊、引用等。
    支持从多种学术API获取的数据进行统一建模。
    
    Attributes:
        paper_id: 统一论文ID
        title: 论文标题
        authors: 作者列表
        journal: 期刊名称
        publish_year: 发表年份
        publish_date: 完整发表日期
        keywords: 关键词列表
        abstract: 摘要
        citations: 被引次数
        references: 参考文献ID列表
        doi: DOI标识符
        url: 论文链接
        volume: 卷号
        issue: 期号
        pages: 页码
        funding: 基金信息
        fields: 研究领域
        source: 数据来源API
        raw_data: 原始数据（用于调试）
    """
    
    paper_id: str
    title: str
    authors: List['Author'] = field(default_factory=list)
    journal: Optional[str] = None
    publish_year: Optional[int] = None
    publish_date: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    abstract: Optional[str] = None
    citations: Optional[int] = None
    references: List[str] = field(default_factory=list)
    doi: Optional[str] = None
    url: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    funding: List[str] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    source: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将Paper对象转换为字典格式
        
        Returns:
            包含论文所有属性的字典
        """
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": [
                a.to_dict() if hasattr(a, 'to_dict') else str(a) 
                for a in self.authors
            ],
            "journal": self.journal,
            "publish_year": self.publish_year,
            "publish_date": self.publish_date,
            "keywords": self.keywords,
            "abstract": self.abstract,
            "citations": self.citations,
            "references": self.references,
            "doi": self.doi,
            "url": self.url,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "funding": self.funding,
            "fields": self.fields,
            "source": self.source
        }
    
    def get_author_names(self) -> List[str]:
        """
        获取所有作者姓名列表
        
        Returns:
            作者姓名列表
        """
        return [a.name for a in self.authors if hasattr(a, 'name')]
    
    def get_first_author(self) -> Optional['Author']:
        """
        获取第一作者
        
        Returns:
            第一作者对象，如果不存在则返回None
        """
        return self.authors[0] if self.authors else None
    
    def __str__(self) -> str:
        """返回论文的字符串表示"""
        authors_str = ", ".join(self.get_author_names()[:3])
        if len(self.authors) > 3:
            authors_str += " et al."
        return f"[{self.paper_id}] {self.title} - {authors_str} ({self.publish_year})"


# 延迟导入以避免循环依赖
from academic_agent.models.author import Author
