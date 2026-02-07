"""
Scopus API适配器模块

Scopus是Elsevier提供的学术数据库API，需要API Key。
文档: https://dev.elsevier.com/
"""

import requests
import time
import logging
from typing import List, Optional, Dict, Any

from academic_agent.adapters.base_adapter import BaseAcademicAdapter
from academic_agent.models import Paper, Author, Journal
from academic_agent.exceptions import (
    APIRequestError, RateLimitExceededError, AuthenticationError,
    PaperNotFoundError, AuthorNotFoundError
)

logger = logging.getLogger(__name__)


class ScopusAdapter(BaseAcademicAdapter):
    """
    Scopus API适配器
    
    Scopus是Elsevier提供的学术数据库，需要API Key进行认证。
    提供论文搜索、作者信息、引证关系等功能。
    
    Attributes:
        api_key: Scopus API密钥
        base_url: API基础URL
        headers: 包含API Key的请求头
        rate_limit: 每秒请求数限制（默认0.8次/秒，约50次/分钟）
    
    Example:
        >>> config = {"api_key": "your_api_key", "rate_limit": 0.8}
        >>> adapter = ScopusAdapter(config)
        >>> papers = adapter.search_papers("machine learning", start_year=2020)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Scopus适配器
        
        Args:
            config: 配置字典
                - api_key: Scopus API密钥（必需）
                - base_url: API基础URL（可选，默认https://api.elsevier.com/content）
                - rate_limit: 每秒请求数限制（默认0.8）
                - retry_times: 重试次数（默认3）
                - retry_delay: 重试延迟（默认1秒）
                - timeout: 请求超时时间（默认30秒）
        """
        super().__init__(config)
        self.base_url = config.get("base_url", "https://api.elsevier.com/content")
        self.api_key = config.get("api_key")
        if not self.api_key:
            logger.warning("Scopus API Key未配置，部分功能可能不可用")
        self.rate_limit = config.get("rate_limit", 0.8)  # 约50次/分钟
        self.headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json"
        }
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        发送HTTP请求，带认证和重试机制
        
        Args:
            endpoint: API端点路径
            params: 查询参数
            
        Returns:
            API响应的JSON数据
            
        Raises:
            AuthenticationError: 认证失败时抛出
            RateLimitExceededError: 频率限制时抛出
            APIRequestError: 请求失败时抛出
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
                
                if response.status_code == 401:
                    raise AuthenticationError("Scopus API认证失败，请检查API Key")
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("X-RateLimit-Reset", 60))
                    logger.warning(f"Scopus频率限制，等待{retry_after}秒")
                    time.sleep(retry_after)
                    continue
                elif response.status_code == 404:
                    return {}
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Scopus请求失败 (尝试 {attempt+1}/{self.retry_times}): {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise APIRequestError(f"Scopus API请求失败: {e}")
        
        return {}
    
    def parse_paper(self, raw_data: Dict[str, Any]) -> Paper:
        """
        将Scopus原始数据解析为Paper对象
        
        Args:
            raw_data: Scopus API返回的数据
            
        Returns:
            解析后的Paper对象
        """
        return self._parse_paper(raw_data)
    
    def _parse_paper(self, data: Dict) -> Paper:
        """
        解析Scopus论文数据为Paper模型
        
        Args:
            data: Scopus abstracts API返回的数据
            
        Returns:
            Paper对象
        """
        coredata = data.get("coredata", {})
        
        # 解析作者列表
        authors = []
        authors_data = data.get("authors", {}).get("author", [])
        if not isinstance(authors_data, list):
            authors_data = [authors_data]
        
        for auth in authors_data:
            # 获取机构信息
            affiliation = None
            affils = auth.get("affiliation", [])
            if affils and len(affils) > 0:
                if isinstance(affils, list):
                    affiliation = affils[0].get("affilname")
                else:
                    affiliation = affils.get("affilname")
            
            authors.append(Author(
                author_id=auth.get("authid", ""),
                name=auth.get("authname", ""),
                affiliation=affiliation,
                source="scopus"
            ))
        
        # 解析关键词
        keywords = []
        authkeywords = coredata.get("authkeywords")
        if authkeywords:
            if isinstance(authkeywords, str):
                keywords = [k.strip() for k in authkeywords.split(" | ")]
            elif isinstance(authkeywords, dict):
                keyword_list = authkeywords.get("author-keyword", [])
                if not isinstance(keyword_list, list):
                    keyword_list = [keyword_list]
                for kw in keyword_list:
                    if isinstance(kw, dict):
                        keywords.append(kw.get("$", ""))
                    elif isinstance(kw, str):
                        keywords.append(kw)
        
        # 获取URL
        url = None
        links = coredata.get("link", [])
        if links:
            if isinstance(links, list):
                for link in links:
                    if isinstance(link, dict) and link.get("@rel") == "scopus":
                        url = link.get("@href")
                        break
            elif isinstance(links, dict):
                url = links.get("@href")
        
        return Paper(
            paper_id=coredata.get("eid", ""),
            title=coredata.get("dc:title", ""),
            authors=authors,
            journal=coredata.get("prism:publicationName", ""),
            publish_year=self._parse_year(coredata.get("prism:coverDate", "")),
            publish_date=coredata.get("prism:coverDate"),
            keywords=keywords,
            abstract=coredata.get("dc:description"),
            citations=int(coredata.get("citedby-count", 0)) if coredata.get("citedby-count") else None,
            doi=coredata.get("prism:doi"),
            url=url,
            volume=coredata.get("prism:volume"),
            issue=coredata.get("prism:issueIdentifier"),
            pages=coredata.get("prism:pageRange"),
            source="scopus",
            raw_data=data
        )
    
    def _parse_year(self, date_str: str) -> Optional[int]:
        """
        从日期字符串解析年份
        
        Args:
            date_str: 日期字符串（格式：YYYY-MM-DD）
            
        Returns:
            年份整数，解析失败则返回None
        """
        if date_str:
            try:
                return int(date_str.split("-")[0])
            except (ValueError, IndexError):
                pass
        return None
    
    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        根据EID获取论文详情
        
        Scopus使用EID格式: 2-s2.0-XXXXXXXXX
        
        Args:
            paper_id: 论文EID
            
        Returns:
            Paper对象，不存在则返回None
            
        Raises:
            APIRequestError: API请求失败时抛出
        """
        # 确保EID格式正确
        if not paper_id.startswith("2-s2.0-"):
            paper_id = f"2-s2.0-{paper_id}"
        
        data = self._make_request(f"abstract/eid/{paper_id}")
        
        if not data or "abstracts-retrieval-response" not in data:
            return None
        
        return self._parse_paper(data["abstracts-retrieval-response"])
    
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
            page_size: 每页数量，默认20，最大25
            
        Returns:
            Paper对象列表
            
        Raises:
            APIRequestError: API请求失败时抛出
        """
        # 构建查询字符串
        query = keyword
        if start_year and end_year:
            query += f" AND PUBYEAR > {start_year-1} AND PUBYEAR < {end_year+1}"
        elif start_year:
            query += f" AND PUBYEAR > {start_year-1}"
        elif end_year:
            query += f" AND PUBYEAR < {end_year+1}"
        
        params = {
            "query": query,
            "count": min(page_size, 25),  # Scopus限制每次最多25条
            "start": (page - 1) * page_size,
            "view": "COMPLETE"
        }
        
        data = self._make_request("search/scopus", params)
        entries = data.get("search-results", {}).get("entry", [])
        
        papers = []
        for entry in entries:
            papers.append(self._parse_search_result(entry))
        
        return papers
    
    def _parse_search_result(self, entry: Dict) -> Paper:
        """
        解析搜索结果条目为Paper对象
        
        搜索结果中的数据格式与摘要API略有不同
        
        Args:
            entry: 搜索结果条目
            
        Returns:
            Paper对象
        """
        # 解析关键词
        keywords = []
        authkeywords = entry.get("authkeywords")
        if authkeywords:
            if isinstance(authkeywords, str):
                keywords = [k.strip() for k in authkeywords.split(" | ")]
        
        # 获取URL
        url = None
        links = entry.get("link", [])
        if links and isinstance(links, list):
            for link in links:
                if isinstance(link, dict) and link.get("@rel") == "scopus":
                    url = link.get("@href")
                    break
        
        return Paper(
            paper_id=entry.get("eid", ""),
            title=entry.get("dc:title", ""),
            authors=[],  # 搜索结果不包含完整作者信息
            journal=entry.get("prism:publicationName", ""),
            publish_year=self._parse_year(entry.get("prism:coverDate", "")),
            publish_date=entry.get("prism:coverDate"),
            keywords=keywords,
            abstract=entry.get("dc:description"),
            citations=int(entry.get("citedby-count", 0)) if entry.get("citedby-count") else None,
            doi=entry.get("prism:doi"),
            url=url,
            source="scopus",
            raw_data=entry
        )
    
    def get_author_papers(
        self, 
        author_id: str, 
        start_year: Optional[int] = None,
        end_year: Optional[int] = None, 
        limit: int = 100
    ) -> List[Paper]:
        """
        获取作者发表的论文列表
        
        Args:
            author_id: 作者ID（Scopus Author ID）
            start_year: 开始年份（可选）
            end_year: 结束年份（可选）
            limit: 返回数量限制，默认100，最大25（Scopus限制）
            
        Returns:
            Paper对象列表
            
        Raises:
            APIRequestError: API请求失败时抛出
        """
        query = f"AU-ID({author_id})"
        if start_year and end_year:
            query += f" AND PUBYEAR > {start_year-1} AND PUBYEAR < {end_year+1}"
        elif start_year:
            query += f" AND PUBYEAR > {start_year-1}"
        elif end_year:
            query += f" AND PUBYEAR < {end_year+1}"
        
        params = {
            "query": query,
            "count": min(limit, 25),  # Scopus限制
            "view": "COMPLETE"
        }
        
        data = self._make_request("search/scopus", params)
        entries = data.get("search-results", {}).get("entry", [])
        
        return [self._parse_search_result(e) for e in entries[:limit]]
    
    def get_author_info(self, author_id: str) -> Optional[Author]:
        """
        获取作者详细信息
        
        Args:
            author_id: 作者ID（Scopus Author ID）
            
        Returns:
            Author对象，不存在则返回None
            
        Raises:
            APIRequestError: API请求失败时抛出
        """
        data = self._make_request(f"author/author_id/{author_id}")
        
        if not data or "author-retrieval-response" not in data:
            return None
        
        response = data["author-retrieval-response"]
        if isinstance(response, list):
            response = response[0]
        
        coredata = response.get("coredata", {})
        profile = response.get("author-profile", {})
        
        # 获取当前机构
        affiliation = None
        current_affil = profile.get("affiliation-current", {})
        if current_affil:
            affiliation = current_affil.get("affiliation-name")
        
        # 获取首选名称
        name = ""
        preferred_name = profile.get("preferred-name", {})
        if preferred_name:
            name = preferred_name.get("indexed-name", "")
        
        return Author(
            author_id=author_id,
            name=name,
            affiliation=affiliation,
            h_index=int(coredata.get("h-index", 0)) if coredata.get("h-index") else None,
            citations=int(coredata.get("citation-count", 0)) if coredata.get("citation-count") else None,
            publications=int(coredata.get("document-count", 0)) if coredata.get("document-count") else None,
            source="scopus"
        )
    
    def get_citation_relations(
        self, 
        paper_id: str, 
        depth: int = 1
    ) -> Dict[str, Any]:
        """
        获取论文的引证关系
        
        Args:
            paper_id: 论文EID
            depth: 引证关系深度（目前只支持1层）
            
        Returns:
            包含引证关系的字典:
                - paper_id: 论文ID
                - references: 该论文引用的论文ID列表（Scopus需要额外权限）
                - citations: 引用该论文的论文ID列表
                - citation_papers: 引用该论文的Paper对象列表
                - citation_count: 引用数量
                
        Raises:
            APIRequestError: API请求失败时抛出
        """
        if not paper_id.startswith("2-s2.0-"):
            paper_id = f"2-s2.0-{paper_id}"
        
        # 获取引用该论文的论文
        params = {"query": f"REF({paper_id})", "count": 100}
        data = self._make_request("search/scopus", params)
        citing_entries = data.get("search-results", {}).get("entry", [])
        
        return {
            "paper_id": paper_id,
            "references": [],  # Scopus获取参考文献需要额外权限
            "citations": [e.get("eid", "") for e in citing_entries],
            "citation_papers": [self._parse_search_result(e) for e in citing_entries],
            "citation_count": len(citing_entries)
        }
    
    def get_journal_info(self, journal_id: str) -> Optional[Journal]:
        """
        获取期刊详细信息
        
        Scopus期刊信息需要通过其他方式获取，当前版本暂未实现。
        
        Args:
            journal_id: 期刊ID
            
        Returns:
            Journal对象，当前版本返回None
        """
        logger.warning("Scopus适配器暂未实现期刊信息获取")
        return None
