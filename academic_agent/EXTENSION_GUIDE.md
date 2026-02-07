# 扩展开发指南

本文档详细介绍了如何为 Academic Agent 添加新的功能扩展，包括API适配器、问答模块、数据处理器等。

## 目录

- [添加新的API适配器](#添加新的api适配器)
- [添加新的问答场景](#添加新的问答场景)
- [添加新的数据处理器](#添加新的数据处理器)
- [添加新的数据格式支持](#添加新的数据格式支持)
- [添加新的数据模型](#添加新的数据模型)
- [最佳实践](#最佳实践)

## 添加新的API适配器

### 概述

Academic Agent 使用适配器模式对接不同的学术API。每个适配器需要继承 `BaseAcademicAdapter` 并实现所有抽象方法。

### 步骤1: 创建适配器文件

在 `adapters/` 目录下创建新的适配器文件：

```python
# adapters/semantic_scholar_adapter.py
"""
Semantic Scholar API 适配器
文档: https://api.semanticscholar.org/api-docs/
"""
from typing import List, Optional, Dict, Any
from academic_agent.adapters.base_adapter import BaseAcademicAdapter
from academic_agent.models import Paper, Author, Journal
from academic_agent.exceptions import APIRequestError, APITimeoutError
import requests
import logging
import time

logger = logging.getLogger(__name__)


class SemanticScholarAdapter(BaseAcademicAdapter):
    """Semantic Scholar API 适配器
    
    Semantic Scholar 是一个免费的学术搜索引擎，提供论文、作者、引用等数据。
    
    Attributes:
        base_url: API基础URL
        api_key: API密钥（可选，但有更高的速率限制）
        session: HTTP会话对象
    """
    
    def __init__(self, config: Dict[str, Any]):
        """初始化适配器
        
        Args:
            config: 配置字典，包含base_url, api_key等
        """
        super().__init__(config)
        self.base_url = config.get("base_url", "https://api.semanticscholar.org/graph/v1")
        self.api_key = config.get("api_key")
        self.session = requests.Session()
        
        # 设置请求头
        headers = {
            "Accept": "application/json",
            "User-Agent": "AcademicAgent/1.0"
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        self.session.headers.update(headers)
        
        logger.info("SemanticScholarAdapter initialized")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """发送HTTP请求
        
        Args:
            endpoint: API端点
            params: 请求参数
            
        Returns:
            API响应数据
            
        Raises:
            APIRequestError: 请求失败时抛出
            APITimeoutError: 请求超时时抛出
        """
        url = f"{self.base_url}/{endpoint}"
        
        # 应用频率限制
        self._apply_rate_limit()
        
        try:
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.config.get("timeout", 30)
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            raise APITimeoutError(f"请求超时: {url}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {url}, error: {e}")
            raise APIRequestError(f"请求失败: {e}")
    
    def _apply_rate_limit(self):
        """应用频率限制"""
        rate_limit = self.config.get("rate_limit", 1.0)  # 默认1秒/请求
        if hasattr(self, '_last_request_time'):
            elapsed = time.time() - self._last_request_time
            if elapsed < rate_limit:
                time.sleep(rate_limit - elapsed)
        self._last_request_time = time.time()
    
    def _parse_paper(self, data: Dict) -> Paper:
        """解析论文数据
        
        Args:
            data: API返回的原始数据
            
        Returns:
            Paper对象
        """
        return Paper(
            id=data.get("paperId"),
            title=data.get("title"),
            abstract=data.get("abstract", ""),
            authors=[a.get("name") for a in data.get("authors", [])],
            author_ids=[a.get("authorId") for a in data.get("authors", []) if a.get("authorId")],
            publish_year=data.get("year"),
            journal=data.get("venue"),
            doi=data.get("externalIds", {}).get("DOI"),
            citations_count=data.get("citationCount", 0),
            references_count=data.get("referenceCount", 0),
            url=data.get("url"),
            keywords=data.get("fieldsOfStudy", []),
            language="en"
        )
    
    def _parse_author(self, data: Dict) -> Author:
        """解析作者数据
        
        Args:
            data: API返回的原始数据
            
        Returns:
            Author对象
        """
        return Author(
            id=data.get("authorId"),
            name=data.get("name"),
            affiliation=data.get("affiliations", [{}])[0].get("name") if data.get("affiliations") else None,
            h_index=data.get("hIndex"),
            citations_count=data.get("citationCount", 0),
            papers_count=data.get("paperCount", 0),
            orcid=None,
            homepage=None,
            email=None
        )
    
    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """根据ID获取论文
        
        Args:
            paper_id: 论文ID
            
        Returns:
            Paper对象，未找到返回None
        """
        try:
            fields = "paperId,title,abstract,year,venue,authors,citationCount,referenceCount,url,fieldsOfStudy,externalIds"
            data = self._make_request(f"paper/{paper_id}", {"fields": fields})
            return self._parse_paper(data)
        except APIRequestError:
            return None
    
    def search_papers(
        self, 
        keyword: str, 
        start_year: int = None, 
        end_year: int = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Paper]:
        """搜索论文
        
        Args:
            keyword: 搜索关键词
            start_year: 开始年份
            end_year: 结束年份
            page: 页码
            page_size: 每页数量
            
        Returns:
            论文列表
        """
        params = {
            "query": keyword,
            "fields": "paperId,title,abstract,year,venue,authors,citationCount,referenceCount,url,fieldsOfStudy",
            "limit": page_size,
            "offset": (page - 1) * page_size
        }
        
        # 添加年份过滤
        if start_year:
            params["publicationDateOrYear"] = f"{start_year}:"
        if end_year:
            params["publicationDateOrYear"] = f"{start_year or ''}:{end_year}"
        
        try:
            data = self._make_request("paper/search", params)
            papers = []
            for item in data.get("data", []):
                papers.append(self._parse_paper(item))
            return papers
        except APIRequestError:
            return []
    
    def get_author_papers(
        self, 
        author_id: str, 
        start_year: int = None, 
        end_year: int = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Paper]:
        """获取作者论文列表
        
        Args:
            author_id: 作者ID
            start_year: 开始年份
            end_year: 结束年份
            page: 页码
            page_size: 每页数量
            
        Returns:
            论文列表
        """
        fields = "papers.paperId,papers.title,papers.abstract,papers.year,papers.venue,papers.citationCount"
        
        try:
            data = self._make_request(
                f"author/{author_id}", 
                {"fields": fields}
            )
            papers = []
            for item in data.get("papers", [])[:page_size]:
                paper = self._parse_paper(item)
                # 年份过滤
                if start_year and paper.publish_year and paper.publish_year < start_year:
                    continue
                if end_year and paper.publish_year and paper.publish_year > end_year:
                    continue
                papers.append(paper)
            return papers
        except APIRequestError:
            return []
    
    def get_author_info(self, author_id: str) -> Optional[Author]:
        """获取作者信息
        
        Args:
            author_id: 作者ID
            
        Returns:
            Author对象，未找到返回None
        """
        fields = "authorId,name,affiliations,hIndex,citationCount,paperCount"
        
        try:
            data = self._make_request(f"author/{author_id}", {"fields": fields})
            return self._parse_author(data)
        except APIRequestError:
            return None
    
    def get_citation_relations(
        self, 
        paper_id: str, 
        direction: str = "both"
    ) -> Dict[str, Any]:
        """获取引证关系
        
        Args:
            paper_id: 论文ID
            direction: 方向 ("cited"被引, "citing"引用, "both"两者)
            
        Returns:
            引证关系字典
        """
        result = {"paper_id": paper_id, "cited_by": [], "citing": []}
        
        fields = "paperId,title,year,authors,citationCount"
        
        try:
            if direction in ("cited", "both"):
                data = self._make_request(
                    f"paper/{paper_id}/citations",
                    {"fields": fields, "limit": 100}
                )
                result["cited_by"] = [
                    {
                        "paper_id": p.get("citingPaper", {}).get("paperId"),
                        "title": p.get("citingPaper", {}).get("title"),
                        "year": p.get("citingPaper", {}).get("year"),
                        "authors": [a.get("name") for a in p.get("citingPaper", {}).get("authors", [])]
                    }
                    for p in data.get("data", [])
                ]
            
            if direction in ("citing", "both"):
                data = self._make_request(
                    f"paper/{paper_id}/references",
                    {"fields": fields, "limit": 100}
                )
                result["citing"] = [
                    {
                        "paper_id": p.get("citedPaper", {}).get("paperId"),
                        "title": p.get("citedPaper", {}).get("title"),
                        "year": p.get("citedPaper", {}).get("year"),
                        "authors": [a.get("name") for a in p.get("citedPaper", {}).get("authors", [])]
                    }
                    for p in data.get("data", [])
                ]
            
            return result
            
        except APIRequestError:
            return result
    
    def get_journal_info(self, journal_id: str) -> Optional[Journal]:
        """获取期刊信息
        
        Args:
            journal_id: 期刊ID
            
        Returns:
            Journal对象，未找到返回None
            
        Note:
            Semantic Scholar API不直接提供期刊信息，返回None
        """
        # Semantic Scholar 不直接支持期刊查询
        logger.warning("Semantic Scholar does not support journal queries directly")
        return None
```

### 步骤2: 注册适配器

在 `adapters/__init__.py` 中注册新适配器：

```python
# adapters/__init__.py
"""适配器模块"""

# 适配器映射表
# 键: 适配器名称
# 值: 适配器类的完整模块路径
adapter_map = {
    "openalex": "academic_agent.adapters.openalex_adapter.OpenAlexAdapter",
    "scopus": "academic_agent.adapters.scopus_adapter.ScopusAdapter",
    "sciencedirect": "academic_agent.adapters.sciencedirect_adapter.ScienceDirectAdapter",
    "semanticscholar": "academic_agent.adapters.semantic_scholar_adapter.SemanticScholarAdapter"  # 添加这一行
}

def get_adapter_class(adapter_name: str):
    """获取适配器类
    
    Args:
        adapter_name: 适配器名称
        
    Returns:
        适配器类
        
    Raises:
        ValueError: 适配器不存在时抛出
    """
    if adapter_name not in adapter_map:
        raise ValueError(f"Unknown adapter: {adapter_name}")
    
    # 动态导入适配器类
    module_path, class_name = adapter_map[adapter_name].rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)
```

### 步骤3: 添加配置

在 `config/config.yaml` 中添加新API的配置：

```yaml
apis:
  # ... 其他API配置
  
  semanticscholar:
    base_url: "https://api.semanticscholar.org/graph/v1"
    api_key: null  # 可选，申请地址: https://www.semanticscholar.org/product/api
    rate_limit: 1.0  # 无API Key约1秒/请求，有API Key约10次/秒
    retry_times: 3
    retry_delay: 1
    timeout: 30
```

### 步骤4: 使用新适配器

```python
from academic_agent import LocalAcademicService

# 初始化服务（使用Semantic Scholar适配器）
service = LocalAcademicService(adapter_name="semanticscholar")

# 搜索论文
results = service.search_papers("machine learning", start_year=2020, page_size=10)
print(f"找到 {len(results)} 篇论文")

# 获取论文详情
paper = service.get_paper_info("649def34f8be52c8b66281af98ae884c09aef38b")
print(f"论文标题: {paper['title']}")

# 获取作者信息
author = service.get_author_info("1740531")
print(f"作者: {author['name']}, H指数: {author['h_index']}")
```

### 步骤5: 编写测试

```python
# tests/test_semantic_scholar_adapter.py
import pytest
from academic_agent.adapters.semantic_scholar_adapter import SemanticScholarAdapter

@pytest.fixture
def adapter():
    config = {
        "base_url": "https://api.semanticscholar.org/graph/v1",
        "rate_limit": 1.0,
        "timeout": 30
    }
    return SemanticScholarAdapter(config)

def test_get_paper_by_id(adapter):
    # 使用已知的论文ID测试
    paper = adapter.get_paper_by_id("649def34f8be52c8b66281af98ae884c09aef38b")
    assert paper is not None
    assert paper.title is not None
    assert paper.id is not None

def test_search_papers(adapter):
    papers = adapter.search_papers("machine learning", page_size=5)
    assert len(papers) > 0
    assert all(p.title for p in papers)

def test_get_author_info(adapter):
    author = adapter.get_author_info("1740531")
    assert author is not None
    assert author.name is not None
```

## 添加新的问答场景

### 概述

问答模块处理不同类型的学术查询请求。每个问答模块需要继承 `BaseQAModule` 并实现 `handle` 方法。

### 步骤1: 创建问答模块

```python
# qa/topic_evolution.py
"""
主题演变分析模块
分析某个研究主题随时间的演变趋势
"""
from typing import Dict, Any, List
from academic_agent.qa.base_qa import BaseQAModule
from academic_agent.models import Paper
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TopicEvolutionModule(BaseQAModule):
    """主题演变分析模块
    
    分析研究主题的演变过程，包括：
    - 主题热度随时间的变化
    - 主题相关关键词的演变
    - 主题研究方向的转变
    
    Attributes:
        adapter: 数据适配器
        config: 配置字典
    """
    
    def __init__(self, adapter, config: Dict[str, Any] = None):
        """初始化模块
        
        Args:
            adapter: 数据适配器实例
            config: 配置字典
        """
        super().__init__(adapter, config)
        logger.info("TopicEvolutionModule initialized")
    
    def handle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理查询请求
        
        Args:
            params: 查询参数
                - type: 查询类型 ("topic_evolution")
                - topic: 研究主题
                - start_year: 开始年份
                - end_year: 结束年份
                
        Returns:
            查询结果字典
        """
        query_type = params.get("type")
        
        handlers = {
            "topic_evolution": self._analyze_topic_evolution,
            "topic_keywords": self._analyze_topic_keywords,
            "topic_research_directions": self._analyze_research_directions
        }
        
        if query_type not in handlers:
            return {
                "code": 400,
                "data": None,
                "msg": f"不支持的查询类型: {query_type}"
            }
        
        try:
            result = handlers[query_type](params)
            return {
                "code": 200,
                "data": result,
                "msg": "success"
            }
        except Exception as e:
            logger.error(f"Topic evolution analysis failed: {e}")
            return {
                "code": 500,
                "data": None,
                "msg": f"分析失败: {str(e)}"
            }
    
    def _analyze_topic_evolution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """分析主题演变
        
        Args:
            params: 查询参数
            
        Returns:
            主题演变分析结果
        """
        topic = params.get("topic")
        start_year = params.get("start_year", 2015)
        end_year = params.get("end_year", 2024)
        
        logger.info(f"Analyzing topic evolution for '{topic}' from {start_year} to {end_year}")
        
        # 获取各年份的论文数据
        yearly_data = defaultdict(lambda: {"count": 0, "citations": 0, "papers": []})
        
        for year in range(start_year, end_year + 1):
            papers = self.adapter.search_papers(
                topic, 
                start_year=year, 
                end_year=year,
                page_size=100
            )
            
            yearly_data[year]["count"] = len(papers)
            yearly_data[year]["citations"] = sum(p.citations_count or 0 for p in papers)
            yearly_data[year]["papers"] = papers
        
        # 计算趋势
        counts = [yearly_data[y]["count"] for y in range(start_year, end_year + 1)]
        trend = self._calculate_trend(counts)
        
        return {
            "topic": topic,
            "period": f"{start_year}-{end_year}",
            "yearly_data": {
                str(year): {
                    "paper_count": yearly_data[year]["count"],
                    "citation_count": yearly_data[year]["citations"]
                }
                for year in range(start_year, end_year + 1)
            },
            "trend": trend,
            "total_papers": sum(counts),
            "peak_year": max(yearly_data.keys(), key=lambda y: yearly_data[y]["count"])
        }
    
    def _analyze_topic_keywords(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """分析主题关键词演变
        
        Args:
            params: 查询参数
            
        Returns:
            关键词演变分析结果
        """
        topic = params.get("topic")
        start_year = params.get("start_year", 2015)
        end_year = params.get("end_year", 2024)
        top_n = params.get("top_n", 10)
        
        # 分阶段分析关键词
        mid_year = (start_year + end_year) // 2
        
        early_papers = self.adapter.search_papers(
            topic, 
            start_year=start_year, 
            end_year=mid_year,
            page_size=100
        )
        
        late_papers = self.adapter.search_papers(
            topic, 
            start_year=mid_year + 1, 
            end_year=end_year,
            page_size=100
        )
        
        # 统计关键词
        early_keywords = self._extract_keywords(early_papers)
        late_keywords = self._extract_keywords(late_papers)
        
        # 找出新兴和衰退的关键词
        emerging = [kw for kw in late_keywords if kw not in early_keywords[:top_n]]
        declining = [kw for kw in early_keywords if kw not in late_keywords[:top_n]]
        
        return {
            "topic": topic,
            "early_period": f"{start_year}-{mid_year}",
            "late_period": f"{mid_year+1}-{end_year}",
            "early_keywords": early_keywords[:top_n],
            "late_keywords": late_keywords[:top_n],
            "emerging_keywords": emerging[:top_n],
            "declining_keywords": declining[:top_n]
        }
    
    def _analyze_research_directions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """分析研究方向演变
        
        Args:
            params: 查询参数
            
        Returns:
            研究方向演变分析结果
        """
        topic = params.get("topic")
        start_year = params.get("start_year", 2015)
        end_year = params.get("end_year", 2024)
        
        # 获取论文并分析研究方向
        papers = self.adapter.search_papers(
            topic, 
            start_year=start_year, 
            end_year=end_year,
            page_size=200
        )
        
        # 按年份分组分析
        directions_by_year = defaultdict(list)
        for paper in papers:
            if paper.publish_year and paper.keywords:
                directions_by_year[paper.publish_year].extend(paper.keywords)
        
        # 统计每年的主要研究方向
        yearly_directions = {}
        for year, keywords in directions_by_year.items():
            keyword_counts = defaultdict(int)
            for kw in keywords:
                keyword_counts[kw] += 1
            top_directions = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            yearly_directions[year] = [kw for kw, _ in top_directions]
        
        return {
            "topic": topic,
            "period": f"{start_year}-{end_year}",
            "yearly_directions": yearly_directions,
            "direction_shift": self._detect_direction_shift(yearly_directions)
        }
    
    def _calculate_trend(self, values: List[int]) -> str:
        """计算趋势
        
        Args:
            values: 数值列表
            
        Returns:
            趋势描述 ("rising", "stable", "declining")
        """
        if len(values) < 2:
            return "stable"
        
        first_half = sum(values[:len(values)//2])
        second_half = sum(values[len(values)//2:])
        
        if second_half > first_half * 1.2:
            return "rising"
        elif second_half < first_half * 0.8:
            return "declining"
        return "stable"
    
    def _extract_keywords(self, papers: List[Paper]) -> List[str]:
        """从论文中提取关键词
        
        Args:
            papers: 论文列表
            
        Returns:
            关键词列表（按频率排序）
        """
        keyword_counts = defaultdict(int)
        for paper in papers:
            if paper.keywords:
                for kw in paper.keywords:
                    keyword_counts[kw] += 1
        return [kw for kw, _ in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)]
    
    def _detect_direction_shift(self, yearly_directions: Dict[int, List[str]]) -> Dict[str, Any]:
        """检测研究方向转变
        
        Args:
            yearly_directions: 每年的研究方向
            
        Returns:
            方向转变分析结果
        """
        years = sorted(yearly_directions.keys())
        if len(years) < 2:
            return {"shift_detected": False}
        
        early_directions = set(yearly_directions[years[0]])
        late_directions = set(yearly_directions[years[-1]])
        
        new_directions = late_directions - early_directions
        abandoned_directions = early_directions - late_directions
        
        return {
            "shift_detected": len(new_directions) > 0 or len(abandoned_directions) > 0,
            "new_directions": list(new_directions),
            "abandoned_directions": list(abandoned_directions),
            "stable_directions": list(early_directions & late_directions)
        }
```

### 步骤2: 注册模块

在 `qa/__init__.py` 中导出：

```python
# qa/__init__.py
"""问答模块"""

from academic_agent.qa.base_qa import BaseQAModule
from academic_agent.qa.basic_query import BasicQueryModule
from academic_agent.qa.statistical_analysis import StatisticalAnalysisModule
from academic_agent.qa.relation_analysis import RelationAnalysisModule
from academic_agent.qa.deep_research import DeepResearchModule
from academic_agent.qa.custom_output import CustomOutputModule
from academic_agent.qa.topic_evolution import TopicEvolutionModule  # 添加这一行

__all__ = [
    "BaseQAModule",
    "BasicQueryModule",
    "StatisticalAnalysisModule",
    "RelationAnalysisModule",
    "DeepResearchModule",
    "CustomOutputModule",
    "TopicEvolutionModule"  # 添加这一行
]
```

### 步骤3: 在服务中集成

在 `services/local_service.py` 中添加：

```python
# services/local_service.py
from academic_agent.qa import (
    BasicQueryModule,
    StatisticalAnalysisModule,
    RelationAnalysisModule,
    DeepResearchModule,
    CustomOutputModule,
    TopicEvolutionModule  # 添加导入
)

class LocalAcademicService:
    def __init__(self, adapter_name: str = "openalex", config: Dict = None):
        # ... 其他初始化代码
        
        # 初始化问答模块
        self.basic_query = BasicQueryModule(self.adapter, processor_config)
        self.statistical_analysis = StatisticalAnalysisModule(self.adapter, processor_config)
        self.relation_analysis = RelationAnalysisModule(self.adapter, processor_config)
        self.deep_research = DeepResearchModule(self.adapter, processor_config)
        self.custom_output = CustomOutputModule(self.adapter, processor_config)
        self.topic_evolution = TopicEvolutionModule(self.adapter, processor_config)  # 添加这一行
    
    # ... 其他方法
    
    def analyze_topic_evolution(
        self, 
        topic: str, 
        start_year: int = 2015, 
        end_year: int = 2024
    ) -> Dict[str, Any]:
        """分析主题演变
        
        Args:
            topic: 研究主题
            start_year: 开始年份
            end_year: 结束年份
            
        Returns:
            主题演变分析结果
        """
        result = self.topic_evolution.handle({
            "type": "topic_evolution",
            "topic": topic,
            "start_year": start_year,
            "end_year": end_year
        })
        return result.get("data", {})
    
    def analyze_topic_keywords(
        self, 
        topic: str, 
        start_year: int = 2015, 
        end_year: int = 2024,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """分析主题关键词演变
        
        Args:
            topic: 研究主题
            start_year: 开始年份
            end_year: 结束年份
            top_n: 返回前N个关键词
            
        Returns:
            关键词演变分析结果
        """
        result = self.topic_evolution.handle({
            "type": "topic_keywords",
            "topic": topic,
            "start_year": start_year,
            "end_year": end_year,
            "top_n": top_n
        })
        return result.get("data", {})
```

### 步骤4: 在HTTP服务中添加端点

在 `services/http_service.py` 中添加：

```python
# services/http_service.py
from pydantic import BaseModel
from typing import Optional

class TopicEvolutionRequest(BaseModel):
    topic: str
    start_year: Optional[int] = 2015
    end_year: Optional[int] = 2024

class TopicKeywordsRequest(BaseModel):
    topic: str
    start_year: Optional[int] = 2015
    end_year: Optional[int] = 2024
    top_n: Optional[int] = 10

# 在create_app函数中添加路由
@app.post("/api/research/topic-evolution")
async def topic_evolution(request: TopicEvolutionRequest):
    """主题演变分析"""
    service = get_service()
    result = service.topic_evolution.handle({
        "type": "topic_evolution",
        "topic": request.topic,
        "start_year": request.start_year,
        "end_year": request.end_year
    })
    return result

@app.post("/api/research/topic-keywords")
async def topic_keywords(request: TopicKeywordsRequest):
    """主题关键词演变分析"""
    service = get_service()
    result = service.topic_evolution.handle({
        "type": "topic_keywords",
        "topic": request.topic,
        "start_year": request.start_year,
        "end_year": request.end_year,
        "top_n": request.top_n
    })
    return result
```

## 添加新的数据处理器

### 步骤1: 创建处理器文件

```python
# processors/data_enricher.py
"""数据增强处理器"""
from typing import List, Dict, Any
from academic_agent.models import Paper, Author
import logging

logger = logging.getLogger(__name__)


class DataEnricher:
    """数据增强处理器
    
    为学术数据添加额外的计算字段和元信息
    
    Attributes:
        config: 处理器配置
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化处理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        logger.info("DataEnricher initialized")
    
    def enrich_papers(self, papers: List[Paper]) -> List[Paper]:
        """增强论文数据
        
        Args:
            papers: 论文列表
            
        Returns:
            增强后的论文列表
        """
        enriched = []
        for paper in papers:
            enriched_paper = self._enrich_paper(paper)
            enriched.append(enriched_paper)
        return enriched
    
    def _enrich_paper(self, paper: Paper) -> Paper:
        """增强单篇论文
        
        Args:
            paper: 论文对象
            
        Returns:
            增强后的论文对象
        """
        # 添加影响力分数
        paper.impact_score = self._calculate_impact_score(paper)
        
        # 添加作者数量等级
        paper.author_count_level = self._classify_author_count(paper)
        
        # 添加引用等级
        paper.citation_level = self._classify_citations(paper)
        
        return paper
    
    def _calculate_impact_score(self, paper: Paper) -> float:
        """计算影响力分数
        
        综合考虑被引次数、发表年份、作者数量等因素
        
        Args:
            paper: 论文对象
            
        Returns:
            影响力分数 (0-100)
        """
        score = 0.0
        
        # 被引次数贡献 (最高50分)
        citations = paper.citations_count or 0
        score += min(citations / 10, 50)
        
        # 发表年份贡献 (最高30分，越新越高)
        if paper.publish_year:
            from datetime import datetime
            current_year = datetime.now().year
            years_ago = current_year - paper.publish_year
            score += max(0, 30 - years_ago * 2)
        
        # 作者数量贡献 (最高20分)
        author_count = len(paper.authors) if paper.authors else 0
        score += min(author_count * 2, 20)
        
        return round(score, 2)
    
    def _classify_author_count(self, paper: Paper) -> str:
        """分类作者数量
        
        Args:
            paper: 论文对象
            
        Returns:
            作者数量等级
        """
        count = len(paper.authors) if paper.authors else 0
        
        if count <= 2:
            return "small"
        elif count <= 5:
            return "medium"
        else:
            return "large"
    
    def _classify_citations(self, paper: Paper) -> str:
        """分类引用等级
        
        Args:
            paper: 论文对象
            
        Returns:
            引用等级
        """
        citations = paper.citations_count or 0
        
        if citations >= 100:
            return "highly_cited"
        elif citations >= 50:
            return "well_cited"
        elif citations >= 10:
            return "cited"
        else:
            return "low_cited"
```

### 步骤2: 在处理器链中集成

```python
# processors/__init__.py
from academic_agent.processors.data_cleaner import DataCleaner
from academic_agent.processors.data_cache import DataCache
from academic_agent.processors.data_converter import DataConverter
from academic_agent.processors.data_enricher import DataEnricher  # 添加导入

__all__ = [
    "DataCleaner",
    "DataCache", 
    "DataConverter",
    "DataEnricher"  # 添加导出
]
```

## 添加新的数据格式支持

### 步骤1: 在DataConverter中添加转换方法

```python
# processors/data_converter.py

class DataConverter:
    """数据格式转换器"""
    
    # ... 其他方法
    
    def to_ris(self, papers: List[Paper]) -> str:
        """转换为RIS格式
        
        RIS (Research Information Systems) 是参考文献管理常用的格式
        
        Args:
            papers: 论文列表
            
        Returns:
            RIS格式字符串
        """
        ris_entries = []
        
        for paper in papers:
            entry = []
            entry.append("TY  - JOUR")  # 类型: 期刊文章
            
            if paper.id:
                entry.append(f"ID  - {paper.id}")
            
            if paper.title:
                entry.append(f"TI  - {paper.title}")
            
            for author in (paper.authors or []):
                entry.append(f"AU  - {author}")
            
            if paper.journal:
                entry.append(f"JO  - {paper.journal}")
            
            if paper.publish_year:
                entry.append(f"PY  - {paper.publish_year}")
            
            if paper.doi:
                entry.append(f"DO  - {paper.doi}")
            
            if paper.abstract:
                entry.append(f"AB  - {paper.abstract}")
            
            if paper.url:
                entry.append(f"UR  - {paper.url}")
            
            entry.append("ER  - ")  # 记录结束
            ris_entries.append("\n".join(entry))
        
        return "\n\n".join(ris_entries)
    
    def to_endnote(self, papers: List[Paper]) -> str:
        """转换为EndNote格式
        
        Args:
            papers: 论文列表
            
        Returns:
            EndNote格式字符串
        """
        # EndNote XML格式
        entries = []
        for paper in papers:
            entry = f"""<record>
    <ref-type name="Journal Article">17</ref-type>
    <titles>
        <title>{self._escape_xml(paper.title or "")}</title>
    </titles>
    <contributors>
        {''.join(f'<author>{self._escape_xml(a)}</author>' for a in (paper.authors or []))}
    </contributors>
    <periodical>
        <full-title>{self._escape_xml(paper.journal or "")}</full-title>
    </periodical>
    <dates>
        <year>{paper.publish_year or ""}</year>
    </dates>
    <urls>
        <web-urls>
            <url>{paper.url or ""}</url>
        </web-urls>
    </urls>
</record>"""
            entries.append(entry)
        
        return f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<xml>\n{''.join(entries)}\n</xml>"
    
    def _escape_xml(self, text: str) -> str:
        """转义XML特殊字符"""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))
    
    def convert(self, data: Any, target_format: str, **kwargs):
        """转换数据格式
        
        Args:
            data: 原始数据
            target_format: 目标格式
            **kwargs: 额外参数
            
        Returns:
            转换后的数据
        """
        converter_map = {
            "json": self.to_json,
            "csv": self.to_csv,
            "excel": self.to_excel,
            "bibtex": self.to_bibtex,
            "ris": self.to_ris,  # 添加RIS格式
            "endnote": self.to_endnote  # 添加EndNote格式
        }
        
        if target_format not in converter_map:
            raise ValueError(f"Unsupported format: {target_format}")
        
        return converter_map[target_format](data, **kwargs)
```

## 添加新的数据模型

### 步骤1: 创建模型文件

```python
# models/conference.py
"""会议数据模型"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Conference:
    """会议数据模型
    
    Attributes:
        id: 会议唯一标识
        name: 会议名称
        abbreviation: 会议缩写
        description: 会议描述
        location: 会议地点
        start_date: 开始日期
        end_date: 结束日期
        website: 会议网站
        papers: 会议论文列表
        organizers: 组织者列表
        sponsors: 赞助商列表
        keywords: 会议关键词
        acceptance_rate: 录用率
        h5_index: H5指数
    """
    
    id: str
    name: str
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    website: Optional[str] = None
    papers: List[str] = field(default_factory=list)  # 论文ID列表
    organizers: List[str] = field(default_factory=list)
    sponsors: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    acceptance_rate: Optional[float] = None
    h5_index: Optional[int] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "abbreviation": self.abbreviation,
            "description": self.description,
            "location": self.location,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "website": self.website,
            "papers_count": len(self.papers),
            "organizers": self.organizers,
            "sponsors": self.sponsors,
            "keywords": self.keywords,
            "acceptance_rate": self.acceptance_rate,
            "h5_index": self.h5_index
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Conference":
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            abbreviation=data.get("abbreviation"),
            description=data.get("description"),
            location=data.get("location"),
            start_date=datetime.fromisoformat(data["start_date"]) if data.get("start_date") else None,
            end_date=datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None,
            website=data.get("website"),
            papers=data.get("papers", []),
            organizers=data.get("organizers", []),
            sponsors=data.get("sponsors", []),
            keywords=data.get("keywords", []),
            acceptance_rate=data.get("acceptance_rate"),
            h5_index=data.get("h5_index")
        )
```

### 步骤2: 在模型模块中导出

```python
# models/__init__.py
"""数据模型模块"""

from academic_agent.models.paper import Paper
from academic_agent.models.author import Author
from academic_agent.models.journal import Journal
from academic_agent.models.conference import Conference  # 添加导入

__all__ = [
    "Paper",
    "Author",
    "Journal",
    "Conference"  # 添加导出
]
```

## 最佳实践

### 1. 代码规范

- 遵循 PEP 8 编码规范
- 使用类型注解
- 编写详细的文档字符串
- 添加适当的日志记录

### 2. 错误处理

```python
from academic_agent.exceptions import APIRequestError, DataProcessingError

def safe_operation(self, params):
    try:
        result = self._do_operation(params)
        return {"code": 200, "data": result, "msg": "success"}
    except APIRequestError as e:
        logger.error(f"API request failed: {e}")
        return {"code": 503, "data": None, "msg": f"API请求失败: {e}"}
    except DataProcessingError as e:
        logger.error(f"Data processing failed: {e}")
        return {"code": 500, "data": None, "msg": f"数据处理失败: {e}"}
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return {"code": 500, "data": None, "msg": f"系统错误: {e}"}
```

### 3. 测试覆盖

- 为每个新功能编写单元测试
- 测试覆盖率目标: 85%+
- 包含正常和异常情况测试

### 4. 文档编写

- 更新 README.md 中的API列表
- 在 DEPLOYMENT.md 中添加相关配置说明
- 编写功能使用示例

### 5. 版本控制

- 使用语义化版本号 (MAJOR.MINOR.PATCH)
- 在 CHANGELOG.md 中记录变更
- 重大变更需要更新文档

---

更多问题请参考 [README.md](./README.md) 或提交 Issue。
