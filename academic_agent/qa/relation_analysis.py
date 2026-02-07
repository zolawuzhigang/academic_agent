"""
关系分析模块

提供学术关系分析功能，包括引证关系、合作网络等
"""

from typing import Dict, Any, List, Set, Optional
from collections import defaultdict

from academic_agent.qa.base_qa import BaseQAModule
from academic_agent.models import Paper


class RelationAnalysisModule(BaseQAModule):
    """
    关系分析模块
    
    提供学术关系分析功能，包括：
    - 引证关系分析
    - 合作网络分析
    - 作者关系分析
    
    Example:
        >>> module = RelationAnalysisModule(adapter)
        >>> result = module.handle({
        ...     "action": "citation_network",
        ...     "paper_id": "W123456"
        ... })
    """
    
    @property
    def module_name(self) -> str:
        """模块名称"""
        return "relation"
    
    @property
    def module_description(self) -> str:
        """模块描述"""
        return "关系分析模块 - 提供引证关系、合作网络等分析功能"
    
    def handle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理关系分析请求
        
        Args:
            params: 请求参数，必须包含"action"字段
            
        Returns:
            标准化响应字典
        """
        self.validate_params(params, ["action"])
        
        action = params["action"]
        
        handlers = {
            "citation_network": self._citation_network,
            "coauthor_network": self._coauthor_network,
            "author_collaboration": self._author_collaboration,
            "paper_influence": self._paper_influence
        }
        
        if action not in handlers:
            return self.error_response(400, f"未知的操作: {action}")
        
        try:
            return handlers[action](params)
        except Exception as e:
            return self.error_response(500, str(e))
    
    def _citation_network(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """引证关系网络分析"""
        self.validate_params(params, ["paper_id"])
        
        paper_id = params["paper_id"]
        depth = params.get("depth", 1)
        
        relations = self.adapter.get_citation_relations(paper_id, depth)
        
        # 构建网络数据
        nodes = []
        edges = []
        
        # 添加中心节点
        center_paper = self.adapter.get_paper_by_id(paper_id)
        if center_paper:
            nodes.append({
                "id": paper_id,
                "label": center_paper.title[:50],
                "type": "center",
                "citations": center_paper.citations or 0
            })
        
        # 添加引用节点
        for ref_id in relations.get("references", []):
            ref_paper = self.adapter.get_paper_by_id(ref_id)
            if ref_paper:
                nodes.append({
                    "id": ref_id,
                    "label": ref_paper.title[:50],
                    "type": "reference",
                    "citations": ref_paper.citations or 0
                })
                edges.append({
                    "source": paper_id,
                    "target": ref_id,
                    "type": "cites"
                })
        
        # 添加被引用节点
        for cite_id in relations.get("citations", []):
            cite_paper = self.adapter.get_paper_by_id(cite_id)
            if cite_paper:
                nodes.append({
                    "id": cite_id,
                    "label": cite_paper.title[:50],
                    "type": "citation",
                    "citations": cite_paper.citations or 0
                })
                edges.append({
                    "source": cite_id,
                    "target": paper_id,
                    "type": "cites"
                })
        
        return self.success_response({
            "paper_id": paper_id,
            "depth": depth,
            "network": {
                "nodes": nodes,
                "edges": edges
            },
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "references_count": len(relations.get("references", [])),
                "citations_count": len(relations.get("citations", []))
            }
        })
    
    def _coauthor_network(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """合作者网络分析"""
        self.validate_params(params, ["author_id"])
        
        author_id = params["author_id"]
        depth = params.get("depth", 1)
        
        papers = self.adapter.get_author_papers(
            author_id=author_id,
            limit=params.get("limit", 200)
        )
        
        # 构建合作者网络
        nodes = []
        edges = []
        author_info = {}
        
        # 添加中心作者
        center_author = self.adapter.get_author_info(author_id)
        if center_author:
            nodes.append({
                "id": author_id,
                "label": center_author.name,
                "type": "center",
                "affiliation": center_author.affiliation
            })
        
        # 收集合作者
        coauthor_papers = defaultdict(list)
        for paper in papers:
            for author in paper.authors:
                if author.author_id != author_id:
                    coauthor_papers[author.author_id].append(paper.paper_id)
                    author_info[author.author_id] = author
        
        # 添加合作者节点
        for coauthor_id, paper_ids in coauthor_papers.items():
            author = author_info.get(coauthor_id)
            if author:
                nodes.append({
                    "id": coauthor_id,
                    "label": author.name,
                    "type": "coauthor",
                    "affiliation": author.affiliation
                })
                edges.append({
                    "source": author_id,
                    "target": coauthor_id,
                    "weight": len(paper_ids),
                    "papers": paper_ids
                })
        
        return self.success_response({
            "author_id": author_id,
            "network": {
                "nodes": nodes,
                "edges": edges
            },
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "total_papers": len(papers)
            }
        })
    
    def _author_collaboration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """多作者合作关系分析"""
        self.validate_params(params, ["author_ids"])
        
        author_ids = params["author_ids"]
        
        # 获取每个作者的论文
        author_papers = {}
        for author_id in author_ids:
            papers = self.adapter.get_author_papers(author_id, limit=500)
            author_papers[author_id] = {p.paper_id for p in papers}
        
        # 计算合作论文
        collaboration_matrix = defaultdict(lambda: defaultdict(int))
        
        for i, author1 in enumerate(author_ids):
            for author2 in author_ids[i+1:]:
                common_papers = author_papers[author1] & author_papers[author2]
                collaboration_matrix[author1][author2] = len(common_papers)
                collaboration_matrix[author2][author1] = len(common_papers)
        
        # 获取作者信息
        author_names = {}
        for author_id in author_ids:
            author = self.adapter.get_author_info(author_id)
            author_names[author_id] = author.name if author else author_id
        
        return self.success_response({
            "author_ids": author_ids,
            "author_names": author_names,
            "collaboration_matrix": dict(collaboration_matrix),
            "total_collaborations": sum(
                collaboration_matrix[a][b] 
                for i, a in enumerate(author_ids)
                for b in author_ids[i+1:]
            )
        })
    
    def _paper_influence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """论文影响力分析"""
        self.validate_params(params, ["paper_id"])
        
        paper_id = params["paper_id"]
        
        paper = self.adapter.get_paper_by_id(paper_id)
        if not paper:
            from academic_agent.exceptions import PaperNotFoundError
            raise PaperNotFoundError(paper_id)
        
        relations = self.adapter.get_citation_relations(paper_id, depth=1)
        
        # 分析引用论文的质量
        citing_papers = []
        total_citations_of_citers = 0
        
        for cite_id in relations.get("citations", [])[:50]:  # 限制数量
            cite_paper = self.adapter.get_paper_by_id(cite_id)
            if cite_paper:
                citing_papers.append({
                    "paper_id": cite_id,
                    "title": cite_paper.title,
                    "citations": cite_paper.citations or 0,
                    "journal": cite_paper.journal,
                    "year": cite_paper.publish_year
                })
                total_citations_of_citers += cite_paper.citations or 0
        
        avg_citations_of_citers = (
            total_citations_of_citers / len(citing_papers)
            if citing_papers else 0
        )
        
        return self.success_response({
            "paper_id": paper_id,
            "title": paper.title,
            "citations": paper.citations or 0,
            "influence_metrics": {
                "direct_citations": len(relations.get("citations", [])),
                "avg_citations_of_citers": avg_citations_of_citers,
                "highly_cited_citers": sum(
                    1 for p in citing_papers if p["citations"] > 100
                )
            },
            "citing_papers": citing_papers[:10]  # 返回前10个
        })
