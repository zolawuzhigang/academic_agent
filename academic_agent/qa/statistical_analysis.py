"""
统计分析模块

提供学术数据的统计分析功能
"""

from typing import Dict, Any, List, Optional
from collections import Counter

from academic_agent.qa.base_qa import BaseQAModule
from academic_agent.models import Paper


class StatisticalAnalysisModule(BaseQAModule):
    """
    统计分析模块
    
    提供学术数据的统计分析功能，包括：
    - 发文量统计
    - 被引量统计
    - 期刊分布统计
    - 年份分布统计
    - 合作者统计
    
    Example:
        >>> module = StatisticalAnalysisModule(adapter)
        >>> result = module.handle({
        ...     "action": "author_publication_stats",
        ...     "author_id": "A123456"
        ... })
    """
    
    @property
    def module_name(self) -> str:
        """模块名称"""
        return "statistical"
    
    @property
    def module_description(self) -> str:
        """模块描述"""
        return "统计分析模块 - 提供学术数据的统计分析功能"
    
    def handle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理统计分析请求
        
        Args:
            params: 请求参数，必须包含"action"字段
            
        Returns:
            标准化响应字典
        """
        self.validate_params(params, ["action"])
        
        action = params["action"]
        
        handlers = {
            "author_publication_stats": self._author_publication_stats,
            "author_citation_stats": self._author_citation_stats,
            "journal_distribution": self._journal_distribution,
            "year_distribution": self._year_distribution,
            "keyword_distribution": self._keyword_distribution,
            "coauthor_stats": self._coauthor_stats
        }
        
        if action not in handlers:
            return self.error_response(400, f"未知的操作: {action}")
        
        try:
            return handlers[action](params)
        except Exception as e:
            return self.error_response(500, str(e))
    
    def _author_publication_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """作者发文量统计"""
        self.validate_params(params, ["author_id"])
        
        papers = self.adapter.get_author_papers(
            author_id=params["author_id"],
            start_year=params.get("start_year"),
            end_year=params.get("end_year"),
            limit=params.get("limit", 1000)
        )
        
        # 按年份统计
        year_counts = Counter()
        for paper in papers:
            if paper.publish_year:
                year_counts[paper.publish_year] += 1
        
        return self.success_response({
            "author_id": params["author_id"],
            "total_publications": len(papers),
            "yearly_distribution": dict(sorted(year_counts.items())),
            "first_publication": min(year_counts.keys()) if year_counts else None,
            "latest_publication": max(year_counts.keys()) if year_counts else None
        })
    
    def _author_citation_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """作者被引量统计"""
        self.validate_params(params, ["author_id"])
        
        papers = self.adapter.get_author_papers(
            author_id=params["author_id"],
            limit=params.get("limit", 1000)
        )
        
        citations = [p.citations for p in papers if p.citations is not None]
        
        if not citations:
            return self.success_response({
                "author_id": params["author_id"],
                "total_citations": 0,
                "average_citations": 0,
                "h_index": 0
            })
        
        # 计算H指数
        sorted_citations = sorted(citations, reverse=True)
        h_index = sum(1 for i, c in enumerate(sorted_citations, 1) if c >= i)
        
        return self.success_response({
            "author_id": params["author_id"],
            "total_citations": sum(citations),
            "average_citations": sum(citations) / len(citations),
            "max_citations": max(citations),
            "min_citations": min(citations),
            "h_index": h_index,
            "publications_with_citations": len(citations)
        })
    
    def _journal_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """期刊分布统计"""
        self.validate_params(params, ["author_id"])
        
        papers = self.adapter.get_author_papers(
            author_id=params["author_id"],
            limit=params.get("limit", 1000)
        )
        
        journal_counts = Counter(p.journal for p in papers if p.journal)
        
        return self.success_response({
            "author_id": params["author_id"],
            "total_journals": len(journal_counts),
            "journal_distribution": dict(
                journal_counts.most_common(params.get("top_n", 10))
            )
        })
    
    def _year_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """年份分布统计"""
        self.validate_params(params, ["keyword"])
        
        papers = self.adapter.search_papers(
            keyword=params["keyword"],
            start_year=params.get("start_year"),
            end_year=params.get("end_year"),
            page_size=params.get("limit", 200)
        )
        
        year_counts = Counter()
        for paper in papers:
            if paper.publish_year:
                year_counts[paper.publish_year] += 1
        
        return self.success_response({
            "keyword": params["keyword"],
            "total_papers": len(papers),
            "yearly_distribution": dict(sorted(year_counts.items()))
        })
    
    def _keyword_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """关键词分布统计"""
        self.validate_params(params, ["author_id"])
        
        papers = self.adapter.get_author_papers(
            author_id=params["author_id"],
            limit=params.get("limit", 1000)
        )
        
        keyword_counts = Counter()
        for paper in papers:
            for keyword in paper.keywords:
                keyword_counts[keyword.lower()] += 1
        
        return self.success_response({
            "author_id": params["author_id"],
            "total_keywords": len(keyword_counts),
            "keyword_distribution": dict(
                keyword_counts.most_common(params.get("top_n", 20))
            )
        })
    
    def _coauthor_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """合作者统计"""
        self.validate_params(params, ["author_id"])
        
        papers = self.adapter.get_author_papers(
            author_id=params["author_id"],
            limit=params.get("limit", 1000)
        )
        
        coauthor_counts = Counter()
        for paper in papers:
            for author in paper.authors:
                if author.author_id != params["author_id"]:
                    coauthor_counts[author.name] += 1
        
        return self.success_response({
            "author_id": params["author_id"],
            "total_coauthors": len(coauthor_counts),
            "total_collaborations": sum(coauthor_counts.values()),
            "top_coauthors": dict(
                coauthor_counts.most_common(params.get("top_n", 10))
            )
        })
