"""
基础查询模块

提供论文、作者、期刊的基础查询功能
"""

from typing import Dict, Any, Optional

from academic_agent.qa.base_qa import BaseQAModule
from academic_agent.exceptions import DataValidationError


class BasicQueryModule(BaseQAModule):
    """
    基础查询模块
    
    提供论文、作者、期刊的基础查询功能，包括：
    - 根据ID获取论文/作者/期刊详情
    - 根据关键词搜索论文
    - 获取作者论文列表
    
    Example:
        >>> module = BasicQueryModule(adapter)
        >>> result = module.handle({
        ...     "action": "search_papers",
        ...     "keyword": "machine learning"
        ... })
    """
    
    @property
    def module_name(self) -> str:
        """模块名称"""
        return "basic"
    
    @property
    def module_description(self) -> str:
        """模块描述"""
        return "基础查询模块 - 提供论文、作者、期刊的基础查询功能"
    
    def handle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理基础查询请求
        
        Args:
            params: 请求参数，必须包含"action"字段：
                - search_papers: 搜索论文
                - get_paper: 获取论文详情
                - get_author: 获取作者详情
                - get_author_papers: 获取作者论文列表
                - get_journal: 获取期刊详情
                
        Returns:
            标准化响应字典
        """
        self.validate_params(params, ["action"])
        
        action = params["action"]
        
        handlers = {
            "search_papers": self._search_papers,
            "get_paper": self._get_paper,
            "get_author": self._get_author,
            "get_author_papers": self._get_author_papers,
            "get_journal": self._get_journal
        }
        
        if action not in handlers:
            return self.error_response(400, f"未知的操作: {action}")
        
        try:
            return handlers[action](params)
        except Exception as e:
            return self.error_response(500, str(e))
    
    def _search_papers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """搜索论文"""
        self.validate_params(params, ["keyword"])
        
        keyword = params["keyword"]
        start_year = params.get("start_year")
        end_year = params.get("end_year")
        page = params.get("page", 1)
        page_size = params.get("page_size", 20)
        
        self.validate_year_range(start_year, end_year)
        
        papers = self.adapter.search_papers(
            keyword=keyword,
            start_year=start_year,
            end_year=end_year,
            page=page,
            page_size=page_size
        )
        
        return self.success_response({
            "papers": [p.to_dict() for p in papers],
            "total": len(papers),
            "page": page,
            "page_size": page_size
        })
    
    def _get_paper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取论文详情"""
        self.validate_params(params, ["paper_id"])
        
        paper = self.adapter.get_paper_by_id(params["paper_id"])
        
        if paper is None:
            from academic_agent.exceptions import PaperNotFoundError
            raise PaperNotFoundError(params["paper_id"])
        
        return self.success_response(paper.to_dict())
    
    def _get_author(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取作者详情"""
        self.validate_params(params, ["author_id"])
        
        author = self.adapter.get_author_info(params["author_id"])
        
        if author is None:
            from academic_agent.exceptions import AuthorNotFoundError
            raise AuthorNotFoundError(params["author_id"])
        
        return self.success_response(author.to_dict())
    
    def _get_author_papers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取作者论文列表"""
        self.validate_params(params, ["author_id"])
        
        papers = self.adapter.get_author_papers(
            author_id=params["author_id"],
            start_year=params.get("start_year"),
            end_year=params.get("end_year"),
            limit=params.get("limit", 100)
        )
        
        return self.success_response({
            "papers": [p.to_dict() for p in papers],
            "total": len(papers)
        })
    
    def _get_journal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取期刊详情"""
        self.validate_params(params, ["journal_id"])
        
        journal = self.adapter.get_journal_info(params["journal_id"])
        
        if journal is None:
            from academic_agent.exceptions import JournalNotFoundError
            raise JournalNotFoundError(params["journal_id"])
        
        return self.success_response(journal.to_dict())
