"""
深度研究模块

提供学术深度研究分析功能
"""

from typing import Dict, Any, List, Optional
from collections import Counter, defaultdict

from academic_agent.qa.base_qa import BaseQAModule


class DeepResearchModule(BaseQAModule):
    """
    深度研究模块
    
    提供学术深度研究分析功能，包括：
    - 研究趋势分析
    - 研究热点识别
    - 研究前沿发现
    - 跨领域分析
    
    Example:
        >>> module = DeepResearchModule(adapter)
        >>> result = module.handle({
        ...     "action": "research_trends",
        ...     "keyword": "machine learning",
        ...     "start_year": 2018,
        ...     "end_year": 2023
        ... })
    """
    
    @property
    def module_name(self) -> str:
        """模块名称"""
        return "deep_research"
    
    @property
    def module_description(self) -> str:
        """模块描述"""
        return "深度研究模块 - 提供研究趋势、热点、前沿等深度分析功能"
    
    def handle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理深度研究请求
        
        Args:
            params: 请求参数，必须包含"action"字段
            
        Returns:
            标准化响应字典
        """
        self.validate_params(params, ["action"])
        
        action = params["action"]
        
        handlers = {
            "research_trends": self._research_trends,
            "research_hotspots": self._research_hotspots,
            "research_frontiers": self._research_frontiers,
            "cross_field_analysis": self._cross_field_analysis,
            "author_research_evolution": self._author_research_evolution
        }
        
        if action not in handlers:
            return self.error_response(400, f"未知的操作: {action}")
        
        try:
            return handlers[action](params)
        except Exception as e:
            return self.error_response(500, str(e))
    
    def _research_trends(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """研究趋势分析"""
        self.validate_params(params, ["keyword"])
        
        keyword = params["keyword"]
        start_year = params.get("start_year", 2010)
        end_year = params.get("end_year", 2023)
        
        # 搜索论文
        papers = []
        for year in range(start_year, end_year + 1):
            year_papers = self.adapter.search_papers(
                keyword=keyword,
                start_year=year,
                end_year=year,
                page_size=100
            )
            papers.extend(year_papers)
        
        # 按年份统计
        year_counts = Counter(p.publish_year for p in papers if p.publish_year)
        
        # 计算增长率
        growth_rates = {}
        sorted_years = sorted(year_counts.keys())
        for i, year in enumerate(sorted_years[1:], 1):
            prev_count = year_counts[sorted_years[i-1]]
            curr_count = year_counts[year]
            if prev_count > 0:
                growth_rates[year] = round(
                    (curr_count - prev_count) / prev_count * 100, 2
                )
        
        # 分析关键词演变
        keyword_evolution = defaultdict(lambda: Counter())
        for paper in papers:
            if paper.publish_year:
                for kw in paper.keywords:
                    keyword_evolution[paper.publish_year][kw.lower()] += 1
        
        return self.success_response({
            "keyword": keyword,
            "period": f"{start_year}-{end_year}",
            "total_papers": len(papers),
            "yearly_distribution": dict(sorted(year_counts.items())),
            "growth_rates": growth_rates,
            "keyword_evolution": {
                str(year): dict(counter.most_common(5))
                for year, counter in sorted(keyword_evolution.items())
            },
            "trend_direction": self._calculate_trend_direction(year_counts)
        })
    
    def _research_hotspots(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """研究热点识别"""
        self.validate_params(params, ["keyword"])
        
        keyword = params["keyword"]
        
        papers = self.adapter.search_papers(
            keyword=keyword,
            start_year=params.get("start_year", 2020),
            end_year=params.get("end_year", 2023),
            page_size=200
        )
        
        # 统计关键词频率
        keyword_counts = Counter()
        for paper in papers:
            for kw in paper.keywords:
                if kw.lower() != keyword.lower():
                    keyword_counts[kw.lower()] += 1
        
        # 统计高被引论文
        highly_cited = [
            {
                "paper_id": p.paper_id,
                "title": p.title,
                "citations": p.citations or 0,
                "year": p.publish_year
            }
            for p in papers
            if p.citations and p.citations > 50
        ]
        highly_cited.sort(key=lambda x: x["citations"], reverse=True)
        
        # 统计活跃期刊
        journal_counts = Counter(p.journal for p in papers if p.journal)
        
        return self.success_response({
            "keyword": keyword,
            "total_papers": len(papers),
            "hot_keywords": dict(keyword_counts.most_common(20)),
            "highly_cited_papers": highly_cited[:10],
            "active_journals": dict(journal_counts.most_common(10))
        })
    
    def _research_frontiers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """研究前沿发现"""
        self.validate_params(params, ["keyword"])
        
        keyword = params["keyword"]
        
        # 获取最新论文
        current_year = 2023  # 使用固定值
        recent_papers = self.adapter.search_papers(
            keyword=keyword,
            start_year=current_year - 2,
            end_year=current_year,
            page_size=100
        )
        
        # 分析新兴关键词
        recent_keywords = Counter()
        for paper in recent_papers:
            for kw in paper.keywords:
                if kw.lower() != keyword.lower():
                    recent_keywords[kw.lower()] += 1
        
        # 识别高影响力新论文
        emerging_papers = [
            {
                "paper_id": p.paper_id,
                "title": p.title,
                "citations": p.citations or 0,
                "year": p.publish_year,
                "authors": [a.name for a in p.authors[:3]]
            }
            for p in recent_papers
            if p.publish_year == current_year and (p.citations or 0) > 10
        ]
        emerging_papers.sort(key=lambda x: x["citations"], reverse=True)
        
        return self.success_response({
            "keyword": keyword,
            "emerging_keywords": dict(recent_keywords.most_common(15)),
            "emerging_papers": emerging_papers[:10],
            "frontier_directions": self._identify_frontier_directions(
                recent_keywords
            )
        })
    
    def _cross_field_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """跨领域分析"""
        self.validate_params(params, ["keywords"])
        
        keywords = params["keywords"]
        
        # 获取每个关键词的论文
        field_papers = {}
        for keyword in keywords:
            papers = self.adapter.search_papers(
                keyword=keyword,
                start_year=params.get("start_year", 2018),
                end_year=params.get("end_year", 2023),
                page_size=100
            )
            field_papers[keyword] = papers
        
        # 计算领域交集
        intersection_analysis = {}
        for i, kw1 in enumerate(keywords):
            for kw2 in keywords[i+1:]:
                papers1 = {p.paper_id for p in field_papers[kw1]}
                papers2 = {p.paper_id for p in field_papers[kw2]}
                intersection = papers1 & papers2
                
                if intersection:
                    intersection_analysis[f"{kw1}_x_{kw2}"] = {
                        "common_papers": len(intersection),
                        "paper_ids": list(intersection)[:10]
                    }
        
        # 统计跨领域作者
        cross_field_authors = Counter()
        for papers in field_papers.values():
            for paper in papers:
                for author in paper.authors:
                    cross_field_authors[author.name] += 1
        
        return self.success_response({
            "keywords": keywords,
            "field_sizes": {
                kw: len(papers) for kw, papers in field_papers.items()
            },
            "intersection_analysis": intersection_analysis,
            "cross_field_authors": dict(
                cross_field_authors.most_common(10)
            )
        })
    
    def _author_research_evolution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """作者研究演变分析"""
        self.validate_params(params, ["author_id"])
        
        author_id = params["author_id"]
        
        papers = self.adapter.get_author_papers(
            author_id=author_id,
            limit=500
        )
        
        # 按年份分组
        papers_by_year = defaultdict(list)
        for paper in papers:
            if paper.publish_year:
                papers_by_year[paper.publish_year].append(paper)
        
        # 分析每年的研究主题
        yearly_topics = {}
        for year, year_papers in sorted(papers_by_year.items()):
            year_keywords = Counter()
            for paper in year_papers:
                for kw in paper.keywords:
                    year_keywords[kw.lower()] += 1
            yearly_topics[year] = dict(year_keywords.most_common(5))
        
        # 分析合作者演变
        yearly_coauthors = defaultdict(set)
        for paper in papers:
            if paper.publish_year:
                for author in paper.authors:
                    if author.author_id != author_id:
                        yearly_coauthors[paper.publish_year].add(author.name)
        
        return self.success_response({
            "author_id": author_id,
            "total_papers": len(papers),
            "career_span": {
                "start": min(papers_by_year.keys()) if papers_by_year else None,
                "end": max(papers_by_year.keys()) if papers_by_year else None
            },
            "yearly_topics": yearly_topics,
            "yearly_coauthor_count": {
                year: len(coauthors)
                for year, coauthors in sorted(yearly_coauthors.items())
            }
        })
    
    def _calculate_trend_direction(self, year_counts: Counter) -> str:
        """计算趋势方向"""
        if len(year_counts) < 2:
            return "insufficient_data"
        
        sorted_years = sorted(year_counts.keys())
        recent = sum(year_counts[y] for y in sorted_years[-3:])
        older = sum(year_counts[y] for y in sorted_years[:3])
        
        if recent > older * 1.5:
            return "rapidly_growing"
        elif recent > older:
            return "growing"
        elif recent < older * 0.5:
            return "declining"
        else:
            return "stable"
    
    def _identify_frontier_directions(self, keywords: Counter) -> List[str]:
        """识别前沿方向"""
        # 这里可以实现更复杂的算法
        top_keywords = [kw for kw, _ in keywords.most_common(10)]
        return top_keywords[:5]
