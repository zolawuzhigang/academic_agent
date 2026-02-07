"""
LLM增强的深度研究模块

使用LLM进行智能化的学术分析
"""

from typing import Dict, Any, List, Optional
from academic_agent.qa.base_qa import BaseQAModule
from academic_agent.adapters import BaseAcademicAdapter
from academic_agent.llm import get_llm_adapter


class LLMEnhancedResearchModule(BaseQAModule):
    """
    LLM增强的深度研究模块
    
    结合学术数据API和LLM，提供智能化的学术分析功能：
    - 智能论文总结
    - 研究趋势分析
    - 研究空白识别
    - 跨领域关联挖掘
    - 论文对比分析
    
    Example:
        >>> module = LLMEnhancedResearchModule(adapter, llm_adapter)
        >>> result = module.handle({
        ...     "type": "smart_summary",
        ...     "paper_ids": ["W1", "W2", "W3"]
        ... })
    """
    
    def __init__(
        self,
        adapter: BaseAcademicAdapter,
        llm_adapter,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化LLM增强模块
        
        Args:
            adapter: 学术API适配器
            llm_adapter: LLM适配器实例
            config: 配置字典
        """
        super().__init__(adapter, config)
        self.llm = llm_adapter
    
    @property
    def module_name(self) -> str:
        """模块名称"""
        return "llm_enhanced_research"
    
    @property
    def module_description(self) -> str:
        """模块描述"""
        return "LLM增强的深度研究模块 - 提供智能化的学术分析功能"
    
    def handle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理LLM增强的请求
        
        Args:
            params: 请求参数
            
        Returns:
            标准化响应字典
        """
        action = params.get("type")
        
        handlers = {
            "smart_summary": self._smart_summary,
            "research_trend_analysis": self._research_trend_analysis,
            "research_gap_identification": self._research_gap_identification,
            "paper_comparison": self._paper_comparison,
            "cross_field_analysis": self._cross_field_analysis,
            "author_research_evolution": self._author_research_evolution,
            "literature_review": self._literature_review
        }
        
        if action not in handlers:
            return self.error_response(400, f"未知的操作: {action}")
        
        try:
            return handlers[action](params)
        except Exception as e:
            return self.error_response(500, str(e))
    
    def _smart_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能论文总结
        
        使用LLM对多篇论文进行智能总结
        """
        paper_ids = params.get("paper_ids", [])
        if not paper_ids:
            return self.error_response(400, "缺少paper_ids参数")
        
        papers = []
        for paper_id in paper_ids[:10]:
            paper = self.adapter.get_paper_by_id(paper_id)
            if paper:
                papers.append(paper.to_dict())
        
        if not papers:
            return self.error_response(404, "未找到指定的论文")
        
        result = self.llm.analyze_papers(papers, "summary")
        
        return self.success_response({
            "papers_count": len(papers),
            "summary": result.get("result"),
            "model": result.get("model"),
            "papers": papers
        })
    
    def _research_trend_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        研究趋势分析
        
        使用LLM分析研究领域的发展趋势
        """
        keyword = params.get("keyword")
        if not keyword:
            return self.error_response(400, "缺少keyword参数")
        
        start_year = params.get("start_year", 2020)
        end_year = params.get("end_year", 2024)
        
        papers = []
        for year in range(start_year, end_year + 1):
            year_papers = self.adapter.search_papers(
                keyword=keyword,
                start_year=year,
                end_year=year,
                page_size=20
            )
            papers.extend([p.to_dict() for p in year_papers])
        
        if not papers:
            return self.error_response(404, "未找到相关论文")
        
        result = self.llm.analyze_papers(papers[:50], "trend")
        
        return self.success_response({
            "keyword": keyword,
            "period": f"{start_year}-{end_year}",
            "papers_count": len(papers),
            "trend_analysis": result.get("result"),
            "model": result.get("model")
        })
    
    def _research_gap_identification(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        研究空白识别
        
        使用LLM识别研究领域的空白和机会
        """
        keyword = params.get("keyword")
        if not keyword:
            return self.error_response(400, "缺少keyword参数")
        
        papers = self.adapter.search_papers(
            keyword=keyword,
            start_year=params.get("start_year", 2020),
            end_year=params.get("end_year", 2024),
            page_size=50
        )
        
        if not papers:
            return self.error_response(404, "未找到相关论文")
        
        result = self.llm.analyze_papers([p.to_dict() for p in papers], "gap")
        
        return self.success_response({
            "keyword": keyword,
            "papers_count": len(papers),
            "research_gaps": result.get("result"),
            "model": result.get("model")
        })
    
    def _paper_comparison(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        论文对比分析
        
        使用LLM对比分析多篇论文
        """
        paper_ids = params.get("paper_ids", [])
        if not paper_ids or len(paper_ids) < 2:
            return self.error_response(400, "需要至少2篇论文进行对比")
        
        papers = []
        for paper_id in paper_ids[:5]:
            paper = self.adapter.get_paper_by_id(paper_id)
            if paper:
                papers.append(paper.to_dict())
        
        if len(papers) < 2:
            return self.error_response(404, "未找到足够的论文进行对比")
        
        result = self.llm.analyze_papers(papers, "compare")
        
        return self.success_response({
            "papers_count": len(papers),
            "comparison": result.get("result"),
            "model": result.get("model"),
            "papers": papers
        })
    
    def _cross_field_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        跨领域关联挖掘
        
        使用LLM分析两个研究领域的交叉点
        """
        field1 = params.get("field1")
        field2 = params.get("field2")
        
        if not field1 or not field2:
            return self.error_response(400, "缺少field1或field2参数")
        
        papers1 = self.adapter.search_papers(field1, page_size=30)
        papers2 = self.adapter.search_papers(field2, page_size=30)
        
        all_papers = [p.to_dict() for p in papers1 + papers2]
        
        prompt = f"""请分析以下两个研究领域的交叉关联：

领域1: {field1}
领域2: {field2}

基于以下论文进行分析：
{self._format_papers_for_llm(all_papers[:20])}

请提供：
1. 两个领域的共同研究主题
2. 交叉研究的技术方法
3. 跨领域应用场景
4. 未来研究方向建议"""
        
        result = self.llm.complete(prompt)
        
        return self.success_response({
            "field1": field1,
            "field2": field2,
            "cross_field_analysis": result.get("content"),
            "model": result.get("model"),
            "papers_count": len(all_papers)
        })
    
    def _author_research_evolution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        作者研究方向演变分析
        
        使用LLM分析作者研究方向的演变
        """
        author_id = params.get("author_id")
        if not author_id:
            return self.error_response(400, "缺少author_id参数")
        
        author = self.adapter.get_author_info(author_id)
        if not author:
            return self.error_response(404, "未找到作者")
        
        papers = self.adapter.get_author_papers(
            author_id=author_id,
            limit=100
        )
        
        if not papers:
            return self.error_response(404, "未找到作者的论文")
        
        papers_dict = [p.to_dict() for p in papers]
        
        prompt = f"""请分析作者 {author.name} 的研究方向演变：

作者信息：
- 机构: {author.affiliation}
- H指数: {author.h_index}
- 论文总数: {len(papers)}

论文列表（按时间排序）：
{self._format_papers_for_llm(papers_dict[:30])}

请提供：
1. 研究主题的演变过程
2. 主要研究阶段和转折点
3. 当前研究焦点
4. 未来可能的研究方向"""
        
        result = self.llm.complete(prompt)
        
        return self.success_response({
            "author_id": author_id,
            "author_name": author.name,
            "papers_count": len(papers),
            "research_evolution": result.get("content"),
            "model": result.get("model")
        })
    
    def _literature_review(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        文献综述生成
        
        使用LLM生成指定主题的文献综述
        """
        topic = params.get("topic")
        if not topic:
            return self.error_response(400, "缺少topic参数")
        
        start_year = params.get("start_year", 2020)
        end_year = params.get("end_year", 2024)
        
        papers = self.adapter.search_papers(
            keyword=topic,
            start_year=start_year,
            end_year=end_year,
            page_size=50
        )
        
        if not papers:
            return self.error_response(404, "未找到相关论文")
        
        papers_dict = [p.to_dict() for p in papers]
        
        prompt = f"""请为以下主题撰写文献综述：

主题: {topic}
时间范围: {start_year}-{end_year}
论文数量: {len(papers_dict)}

请基于以下论文撰写综述：
{self._format_papers_for_llm(papers_dict[:30])}

文献综述应包含：
1. 研究背景和意义
2. 主要研究方法和技术
3. 关键发现和进展
4. 研究局限和不足
5. 未来研究方向
6. 主要参考文献"""
        
        result = self.llm.complete(prompt)
        
        return self.success_response({
            "topic": topic,
            "period": f"{start_year}-{end_year}",
            "papers_count": len(papers_dict),
            "literature_review": result.get("content"),
            "model": result.get("model"),
            "references": papers_dict
        })
    
    def _format_papers_for_llm(self, papers: List[Dict[str, Any]]) -> str:
        """
        格式化论文列表供LLM使用
        
        Args:
            papers: 论文列表
            
        Returns:
            格式化后的文本
        """
        return "\n\n".join([
            f"{i+1}. {p.get('title', 'N/A')}\n"
            f"   作者: {', '.join(p.get('authors', [])[:3])}\n"
            f"   年份: {p.get('publish_year')}\n"
            f"   期刊: {p.get('journal', 'N/A')}\n"
            f"   摘要: {p.get('abstract', 'N/A')[:200]}..."
            for i, p in enumerate(papers)
        ])
