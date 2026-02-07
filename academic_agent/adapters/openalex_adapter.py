"""
OpenAlex API适配器模块

OpenAlex是开放的学术数据API，无需认证即可使用。
文档: https://docs.openalex.org/
"""

import requests
import time
import logging
from typing import List, Optional, Dict, Any

from academic_agent.adapters.base_adapter import BaseAcademicAdapter
from academic_agent.models import Paper, Author, Journal
from academic_agent.exceptions import (
    APIRequestError, RateLimitExceededError,
    PaperNotFoundError, AuthorNotFoundError
)

logger = logging.getLogger(__name__)


class OpenAlexAdapter(BaseAcademicAdapter):
    """
    OpenAlex API适配器
    
    OpenAlex是一个免费的开放学术数据API，提供论文、作者、机构、
    期刊等学术实体的完整数据。无需API Key即可使用。
    
    Attributes:
        base_url: OpenAlex API基础URL
        headers: 请求头，包含User-Agent
        rate_limit: 每秒请求数限制（默认10次/秒）
    
    Example:
        >>> config = {"rate_limit": 10}
        >>> adapter = OpenAlexAdapter(config)
        >>> paper = adapter.get_paper_by_id("W123456789")
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化OpenAlex适配器
        
        Args:
            config: 配置字典
                - base_url: API基础URL（可选，默认https://api.openalex.org）
                - rate_limit: 每秒请求数限制（默认10）
                - retry_times: 重试次数（默认3）
                - retry_delay: 重试延迟（默认1秒）
                - timeout: 请求超时时间（默认30秒）
        """
        super().__init__(config)
        self.base_url = config.get("base_url", "https://api.openalex.org")
        self.rate_limit = config.get("rate_limit", 10)  # 10次/秒
        self.headers = {
            "User-Agent": "AcademicAgent/1.0 (mailto:your@email.com)"
        }
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        发送HTTP请求，带频率限制和重试机制
        
        Args:
            endpoint: API端点路径
            params: 查询参数
            
        Returns:
            API响应的JSON数据
            
        Raises:
            APIRequestError: 请求失败时抛出
            RateLimitExceededError: 频率限制时抛出
        """
        self._rate_limit_wait()
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.retry_times):
            try:
                response = requests.get(
                    url, 
                    params=params, 
                    headers=self.headers, 
                    timeout=self.timeout
                )
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"OpenAlex频率限制，等待{retry_after}秒")
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"OpenAlex请求失败 (尝试 {attempt+1}/{self.retry_times}): {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise APIRequestError(f"OpenAlex API请求失败: {e}")
        
        return {}
    
    def parse_paper(self, raw_data: Dict[str, Any]) -> Paper:
        """
        将OpenAlex原始数据解析为Paper对象
        
        Args:
            raw_data: OpenAlex API返回的works数据
            
        Returns:
            解析后的Paper对象
        """
        return self._parse_paper(raw_data)
    
    def _parse_paper(self, data: Dict) -> Paper:
        """
        解析OpenAlex论文数据为Paper模型
        
        OpenAlex works数据结构参考:
        https://docs.openalex.org/api-entities/works
        
        Args:
            data: OpenAlex works API返回的数据
            
        Returns:
            Paper对象
        """
        # 解析作者列表
        authors = []
        for auth in data.get("authorships", []):
            author_info = auth.get("author", {})
            author_id = author_info.get("id", "")
            if author_id:
                author_id = author_id.split("/")[-1]
            
            # 获取机构信息
            affiliation = None
            institutions = auth.get("institutions", [])
            if institutions and len(institutions) > 0:
                affiliation = institutions[0].get("display_name")
            
            authors.append(Author(
                author_id=author_id,
                name=author_info.get("display_name", ""),
                affiliation=affiliation,
                source="openalex"
            ))
        
        # 提取期刊信息
        journal = None
        primary_location = data.get("primary_location", {})
        if primary_location:
            source = primary_location.get("source", {})
            if source:
                journal = source.get("display_name")
        
        # 如果primary_location没有，尝试host_venue（旧版API）
        if not journal:
            host_venue = data.get("host_venue", {})
            if host_venue:
                journal = host_venue.get("display_name")
        
        # 提取年份
        year = data.get("publication_year")
        if not year and data.get("publication_date"):
            try:
                year = int(data["publication_date"].split("-")[0])
            except (ValueError, IndexError):
                year = None
        
        # 提取关键词/概念
        keywords = []
        for concept in data.get("concepts", []):
            display_name = concept.get("display_name")
            if display_name:
                keywords.append(display_name)
        
        # 提取参考文献
        references = []
        for ref in data.get("referenced_works", []):
            if ref:
                ref_id = ref.split("/")[-1] if "/" in ref else ref
                references.append(ref_id)
        
        return Paper(
            paper_id=data.get("id", "").split("/")[-1] if data.get("id") else "",
            title=data.get("display_name", ""),
            authors=authors,
            journal=journal,
            publish_year=year,
            publish_date=data.get("publication_date"),
            keywords=keywords,
            abstract=self._get_abstract(data),
            citations=data.get("cited_by_count"),
            references=references,
            doi=data.get("doi"),
            url=data.get("id"),
            volume=None,  # OpenAlex不直接提供
            issue=None,
            pages=None,
            source="openalex",
            raw_data=data
        )
    
    def _get_abstract(self, data: Dict) -> Optional[str]:
        """
        获取摘要（OpenAlex摘要是反转索引格式）
        
        OpenAlex使用反转索引存储摘要以节省空间，需要转换回文本。
        
        Args:
            data: OpenAlex works数据
            
        Returns:
            摘要文本，如果不存在则返回None
        """
        abstract_inverted = data.get("abstract_inverted_index")
        if abstract_inverted:
            # 将反转索引转换为文本
            max_pos = max(max(positions) for positions in abstract_inverted.values())
            words = [""] * (max_pos + 1)
            for word, positions in abstract_inverted.items():
                for pos in positions:
                    words[pos] = word
            return " ".join(words)
        return data.get("abstract")
    
    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        根据ID获取论文详情
        
        OpenAlex ID格式: W123456789 或 https://openalex.org/W123456789
        
        Args:
            paper_id: 论文ID
            
        Returns:
            Paper对象，不存在则返回None
            
        Raises:
            APIRequestError: API请求失败时抛出
        """
        # 处理URL格式的ID
        if paper_id.startswith("https://"):
            paper_id = paper_id.split("/")[-1]
        
        data = self._make_request(f"works/{paper_id}")
        if not data or "id" not in data:
            return None
        return self._parse_paper(data)
    
    def search_papers(
        self, 
        keyword: str, 
        start_year: Optional[int] = None,
        end_year: Optional[int] = None, 
        page: int = 1,
        page_size: int = 20
    ) -> List[Paper]:
        """
        根据关键词搜索论文
        
        Args:
            keyword: 搜索关键词
            start_year: 开始年份（可选）
            end_year: 结束年份（可选）
            page: 页码，默认1
            page_size: 每页数量，默认20，最大200
            
        Returns:
            Paper对象列表
            
        Raises:
            APIRequestError: API请求失败时抛出
        """
        params = {
            "search": keyword,
            "per-page": min(page_size, 200),
            "page": page
        }
        
        # 年份过滤
        filter_parts = []
        if start_year and end_year:
            filter_parts.append(f"publication_year:{start_year}-{end_year}")
        elif start_year:
            filter_parts.append(f"publication_year:{start_year}-")
        elif end_year:
            filter_parts.append(f"publication_year:-{end_year}")
        
        if filter_parts:
            params["filter"] = ",".join(filter_parts)
        
        data = self._make_request("works", params)
        results = data.get("results", [])
        return [self._parse_paper(r) for r in results]
    
    def get_author_papers(
        self, 
        author_id: str, 
        start_year: Optional[int] = None,
        end_year: Optional[int] = None, 
        limit: int = 100
    ) -> List[Paper]:
        """
        获取作者发表的论文列表
        
        OpenAlex作者ID格式: A123456789
        
        Args:
            author_id: 作者ID
            start_year: 开始年份（可选）
            end_year: 结束年份（可选）
            limit: 返回数量限制，默认100，最大200
            
        Returns:
            Paper对象列表
            
        Raises:
            APIRequestError: API请求失败时抛出
        """
        # 处理URL格式的ID
        if author_id.startswith("https://"):
            author_id = author_id.split("/")[-1]
        
        filter_parts = [f"author.id:{author_id}"]
        if start_year and end_year:
            filter_parts.append(f"publication_year:{start_year}-{end_year}")
        elif start_year:
            filter_parts.append(f"publication_year:>={start_year}")
        elif end_year:
            filter_parts.append(f"publication_year:<={end_year}")
        
        params = {
            "filter": ",".join(filter_parts),
            "per-page": min(limit, 200),
            "page": 1
        }
        
        all_papers = []
        while len(all_papers) < limit:
            data = self._make_request("works", params)
            results = data.get("results", [])
            if not results:
                break
            all_papers.extend([self._parse_paper(r) for r in results])
            
            # 检查是否还有更多结果
            meta = data.get("meta", {})
            if len(all_papers) >= meta.get("count", 0):
                break
            
            params["page"] += 1
        
        return all_papers[:limit]
    
    def get_author_info(self, author_id: str) -> Optional[Author]:
        """
        获取作者详细信息
        
        Args:
            author_id: 作者ID
            
        Returns:
            Author对象，不存在则返回None
            
        Raises:
            APIRequestError: API请求失败时抛出
        """
        if author_id.startswith("https://"):
            author_id = author_id.split("/")[-1]
        
        data = self._make_request(f"authors/{author_id}")
        if not data or "id" not in data:
            return None
        
        last_inst = data.get("last_known_institution", {})
        summary_stats = data.get("summary_stats", {})
        
        # 提取研究领域
        fields = []
        for concept in data.get("x_concepts", [])[:5]:
            display_name = concept.get("display_name")
            if display_name:
                fields.append(display_name)
        
        return Author(
            author_id=data.get("id", "").split("/")[-1],
            name=data.get("display_name", ""),
            affiliation=last_inst.get("display_name"),
            h_index=summary_stats.get("h_index"),
            citations=data.get("cited_by_count"),
            publications=data.get("works_count"),
            orcid=data.get("orcid"),
            fields=fields,
            source="openalex"
        )
    
    def get_citation_relations(
        self, 
        paper_id: str, 
        depth: int = 1
    ) -> Dict[str, Any]:
        """
        获取论文的引证关系
        
        Args:
            paper_id: 论文ID
            depth: 引证关系深度（目前只支持1层）
            
        Returns:
            包含引证关系的字典:
                - paper_id: 论文ID
                - references: 该论文引用的论文ID列表
                - citations: 引用该论文的论文ID列表
                - citation_papers: 引用该论文的Paper对象列表
                - citation_count: 引用数量
                
        Raises:
            PaperNotFoundError: 论文不存在时抛出
            APIRequestError: API请求失败时抛出
        """
        if paper_id.startswith("https://"):
            paper_id = paper_id.split("/")[-1]
        
        # 获取论文详情
        paper = self.get_paper_by_id(paper_id)
        if not paper:
            raise PaperNotFoundError(f"论文不存在: {paper_id}")
        
        # 获取引用该论文的论文
        params = {
            "filter": f"cites:{paper_id}",
            "per-page": 100
        }
        citing_data = self._make_request("works", params)
        citing_papers = [self._parse_paper(r) for r in citing_data.get("results", [])]
        
        return {
            "paper_id": paper_id,
            "references": paper.references or [],
            "citations": [p.paper_id for p in citing_papers],
            "citation_papers": citing_papers,
            "citation_count": len(citing_papers)
        }
    
    def get_journal_info(self, journal_id: str) -> Optional[Journal]:
        """
        获取期刊详细信息
        
        Args:
            journal_id: 期刊ID（OpenAlex sources ID）
            
        Returns:
            Journal对象，不存在则返回None
            
        Raises:
            APIRequestError: API请求失败时抛出
        """
        if journal_id.startswith("https://"):
            journal_id = journal_id.split("/")[-1]
        
        data = self._make_request(f"sources/{journal_id}")
        if not data or "id" not in data:
            return None
        
        # 获取ISSN
        issn = data.get("issn_l")
        if not issn and data.get("issn"):
            issn_list = data.get("issn")
            if isinstance(issn_list, list) and len(issn_list) > 0:
                issn = issn_list[0]
        
        # 提取研究领域
        fields = []
        for concept in data.get("x_concepts", [])[:5]:
            display_name = concept.get("display_name")
            if display_name:
                fields.append(display_name)
        
        return Journal(
            journal_id=data.get("id", "").split("/")[-1],
            name=data.get("display_name", ""),
            issn=issn,
            publisher=data.get("host_organization_name"),
            impact_factor=None,  # OpenAlex不直接提供影响因子
            cite_score=data.get("summary_stats", {}).get("2yr_mean_citedness"),
            fields=fields,
            source="openalex"
        )
