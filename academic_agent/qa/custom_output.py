"""
自定义输出模块

提供学术数据的自定义格式化输出功能
"""

from typing import Dict, Any, List, Optional

from academic_agent.qa.base_qa import BaseQAModule
from academic_agent.processors import DataConverter


class CustomOutputModule(BaseQAModule):
    """
    自定义输出模块
    
    提供学术数据的自定义格式化输出功能，包括：
    - 多种格式导出（JSON、CSV、Excel）
    - 自定义字段选择
    - 格式化模板
    
    Example:
        >>> module = CustomOutputModule(adapter)
        >>> result = module.handle({
        ...     "action": "export_papers",
        ...     "paper_ids": ["W1", "W2", "W3"],
        ...     "format": "csv",
        ...     "fields": ["title", "authors", "year"]
        ... })
    """
    
    @property
    def module_name(self) -> str:
        """模块名称"""
        return "custom_output"
    
    @property
    def module_description(self) -> str:
        """模块描述"""
        return "自定义输出模块 - 提供多种格式的数据导出功能"
    
    def handle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理自定义输出请求
        
        Args:
            params: 请求参数，必须包含"action"字段
            
        Returns:
            标准化响应字典
        """
        self.validate_params(params, ["action"])
        
        action = params["action"]
        
        handlers = {
            "export_papers": self._export_papers,
            "export_author_profile": self._export_author_profile,
            "format_bibliography": self._format_bibliography,
            "generate_report": self._generate_report
        }
        
        if action not in handlers:
            return self.error_response(400, f"未知的操作: {action}")
        
        try:
            return handlers[action](params)
        except Exception as e:
            return self.error_response(500, str(e))
    
    def _export_papers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """导出论文数据"""
        self.validate_params(params, ["paper_ids", "format"])
        
        paper_ids = params["paper_ids"]
        output_format = params["format"].lower()
        fields = params.get("fields")
        
        # 获取论文数据
        papers = []
        for paper_id in paper_ids:
            paper = self.adapter.get_paper_by_id(paper_id)
            if paper:
                papers.append(paper)
        
        if not papers:
            return self.error_response(404, "未找到指定的论文")
        
        # 根据格式导出
        if output_format == "json":
            data = DataConverter.to_json(papers, indent=2)
        elif output_format == "csv":
            data = DataConverter.papers_to_csv(papers, fields)
        elif output_format == "dict":
            data = [p.to_dict() for p in papers]
        else:
            return self.error_response(400, f"不支持的格式: {output_format}")
        
        return self.success_response({
            "format": output_format,
            "total_papers": len(papers),
            "data": data
        })
    
    def _export_author_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """导出作者档案"""
        self.validate_params(params, ["author_id"])
        
        author_id = params["author_id"]
        
        # 获取作者信息
        author = self.adapter.get_author_info(author_id)
        if not author:
            from academic_agent.exceptions import AuthorNotFoundError
            raise AuthorNotFoundError(author_id)
        
        # 获取作者论文
        papers = self.adapter.get_author_papers(author_id, limit=500)
        
        # 构建档案
        profile = {
            "author_info": author.to_dict(),
            "statistics": {
                "total_publications": len(papers),
                "total_citations": sum(
                    p.citations or 0 for p in papers
                ),
                "publication_years": sorted(
                    set(p.publish_year for p in papers if p.publish_year)
                ),
                "journals": list(set(
                    p.journal for p in papers if p.journal
                )),
                "fields": list(set(
                    field for p in papers for field in p.fields
                ))
            },
            "publications": [p.to_dict() for p in papers[:50]]  # 限制数量
        }
        
        return self.success_response(profile)
    
    def _format_bibliography(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """格式化参考文献"""
        self.validate_params(params, ["paper_ids", "style"])
        
        paper_ids = params["paper_ids"]
        style = params["style"].lower()
        
        papers = []
        for paper_id in paper_ids:
            paper = self.adapter.get_paper_by_id(paper_id)
            if paper:
                papers.append(paper)
        
        formatted = []
        for paper in papers:
            if style == "apa":
                formatted.append(self._format_apa(paper))
            elif style == "mla":
                formatted.append(self._format_mla(paper))
            elif style == "ieee":
                formatted.append(self._format_ieee(paper))
            elif style == "gb":
                formatted.append(self._format_gb(paper))
            else:
                formatted.append(self._format_default(paper))
        
        return self.success_response({
            "style": style,
            "bibliography": formatted
        })
    
    def _generate_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成研究报告"""
        self.validate_params(params, ["keyword"])
        
        keyword = params["keyword"]
        
        # 搜索论文
        papers = self.adapter.search_papers(
            keyword=keyword,
            start_year=params.get("start_year", 2018),
            end_year=params.get("end_year", 2023),
            page_size=100
        )
        
        # 生成报告
        from collections import Counter
        
        year_counts = Counter(p.publish_year for p in papers if p.publish_year)
        journal_counts = Counter(p.journal for p in papers if p.journal)
        keyword_counts = Counter(
            kw.lower() for p in papers for kw in p.keywords
            if kw.lower() != keyword.lower()
        )
        
        # 高被引论文
        highly_cited = sorted(
            [p for p in papers if p.citations and p.citations > 20],
            key=lambda x: x.citations or 0,
            reverse=True
        )[:10]
        
        report = {
            "title": f"{keyword} 研究报告",
            "period": f"{params.get('start_year', 2018)}-{params.get('end_year', 2023)}",
            "summary": {
                "total_papers": len(papers),
                "yearly_distribution": dict(sorted(year_counts.items())),
                "top_journals": dict(journal_counts.most_common(10)),
                "related_keywords": dict(keyword_counts.most_common(15))
            },
            "highly_cited_papers": [
                {
                    "title": p.title,
                    "authors": [a.name for a in p.authors[:3]],
                    "year": p.publish_year,
                    "citations": p.citations,
                    "journal": p.journal
                }
                for p in highly_cited
            ]
        }
        
        return self.success_response(report)
    
    def _format_apa(self, paper) -> str:
        """APA格式"""
        authors = ", ".join([a.name for a in paper.authors[:6]])
        if len(paper.authors) > 6:
            authors += " et al."
        
        return f"{authors} ({paper.publish_year}). {paper.title}. {paper.journal or 'Unknown'}."
    
    def _format_mla(self, paper) -> str:
        """MLA格式"""
        authors = ", ".join([a.name for a in paper.authors[:2]])
        if len(paper.authors) > 2:
            authors += ", et al."
        
        return f'"{paper.title}." {paper.journal or "Unknown"}, {paper.publish_year}.'
    
    def _format_ieee(self, paper) -> str:
        """IEEE格式"""
        authors = ", ".join([a.name for a in paper.authors[:6]])
        if len(paper.authors) > 6:
            authors += " et al."
        
        return f"{authors}, \"{paper.title},\" {paper.journal or 'Unknown'}, {paper.publish_year}."
    
    def _format_gb(self, paper) -> str:
        """GB/T 7714格式"""
        authors = ", ".join([a.name for a in paper.authors[:3]])
        if len(paper.authors) > 3:
            authors += ", 等"
        
        return f"{authors}. {paper.title}[J]. {paper.journal or 'Unknown'}, {paper.publish_year}."
    
    def _format_default(self, paper) -> str:
        """默认格式"""
        authors = ", ".join([a.name for a in paper.authors[:3]])
        if len(paper.authors) > 3:
            authors += ", et al."
        
        return f"[{paper.paper_id}] {authors}. {paper.title}. {paper.journal or 'Unknown'} ({paper.publish_year})"
