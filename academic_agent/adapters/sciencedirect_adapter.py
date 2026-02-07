"""
ScienceDirect API适配器模块

ScienceDirect是Elsevier提供的全文文献API，需要API Key。
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


class ScienceDirectAdapter(BaseAcademicAdapter):
    """
    ScienceDirect API适配器
    
    ScienceDirect是Elsevier提供的全文文献数据库，需要API Key。
    主要用于获取论文全文内容，支持DOI、PII、EID等多种ID格式。
    
    Attributes:
        api_key: ScienceDirect API密钥
        base_url: API基础URL
        headers: 包含API Key的请求头
        rate_limit: 每秒请求数限制（默认0.5次/秒，约30次/分钟）
    
    Example:
        >>> config = {"api_key": "your_api_key", "rate_limit": 0.5}
        >>> adapter = ScienceDirectAdapter(config)
        >>> paper = adapter.get_paper_by_id("10.1016/j.example.2023.01.001")
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化ScienceDirect适配器
        
        Args:
            config: 配置字典
                - api_key: ScienceDirect API密钥（必需）
                - base_url: API基础URL（可选，默认https://api.elsevier.com/content）
                - rate_limit: 每秒请求数限制（默认0.5）
                - retry_times: 重试次数（默认3）
                - retry_delay: 重试延迟（默认1秒）
                - timeout: 请求超时时间（默认30秒）
        """
        super().__init__(config)
        self.base_url = config.get("base_url", "https://api.elsevier.com/content")
        self.api_key = config.get("api_key")
        if not self.api_key:
            logger.warning("ScienceDirect API Key未配置，部分功能可能不可用")
        self.rate_limit = config.get("rate_limit", 0.5)  # 约30次/分钟
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
                    raise AuthenticationError("ScienceDirect API认证失败，请检查API Key")
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("X-RateLimit-Reset", 60))
                    logger.warning(f"ScienceDirect频率限制，等待{retry_after}秒")
                    time.sleep(retry_after)
                    continue
                elif response.status_code == 404:
                    return {}
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"ScienceDirect请求失败 (尝试 {attempt+1}/{self.retry_times}): {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise APIRequestError(f"ScienceDirect API请求失败: {e}")
        
        return {}
    
    def parse_paper(self, raw_data: Dict[str, Any]) -> Paper:
        """
        将ScienceDirect原始数据解析为Paper对象
        
        Args:
            raw_data: ScienceDirect API返回的数据
            
        Returns:
            解析后的Paper对象
        """
        return self._parse_paper(raw_data)
    
    def _parse_paper(self, data: Dict) -> Paper:
        """
        解析ScienceDirect论文数据为Paper模型
        
        Args:
            data: ScienceDirect full-text API返回的数据
            
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
            author_name = auth.get("$", "")
            if not author_name and isinstance(auth, dict):
                # 尝试其他格式
                given_name = auth.get("given-name", "")
                surname = auth.get("surname", "")
                if given_name or surname:
                    author_name = f"{given_name} {surname}".strip()
            
            authors.append(Author(
                author_id=auth.get("@id", ""),
                name=author_name,
                source="sciencedirect"
            ))
        
        # 解析关键词/主题领域
        keywords = []
        subject_areas = data.get("subject-areas", {})
        if subject_areas:
            subject_list = subject_areas.get("subject-area", [])
            if not isinstance(subject_list, list):
                subject_list = [subject_list]
            for subject in subject_list:
                if isinstance(subject, dict):
                    keywords.append(subject.get("$", ""))
        
        # 获取URL
        url = None
        links = coredata.get("link", [])
        if links:
            if isinstance(links, list):
                for link in links:
                    if isinstance(link, dict):
                        url = link.get("@href")
                        break
            elif isinstance(links, dict):
                url = links.get("@href")
        
        # 获取摘要
        abstract = data.get("abstract", "")
        if isinstance(abstract, dict):
            # 处理结构化摘要
            abstract_text = abstract.get("abstract-sec", {})
            if isinstance(abstract_text, dict):
                abstract = abstract_text.get("simple-para", "")
                if isinstance(abstract, dict):
                    abstract = abstract.get("$", "")
        
        # 获取论文ID
        paper_id = coredata.get("eid", "")
        if not paper_id:
            paper_id = coredata.get("dc:identifier", "").replace("doi:", "")
        
        return Paper(
            paper_id=paper_id,
            title=coredata.get("dc:title", ""),
            authors=authors,
            journal=coredata.get("prism:publicationName", ""),
            publish_year=self._parse_year(coredata.get("prism:coverDate", "")),
            publish_date=coredata.get("prism:coverDate"),
            keywords=keywords,
            abstract=abstract if isinstance(abstract, str) else "",
            doi=coredata.get("prism:doi"),
            url=url,
            volume=coredata.get("prism:volume"),
            issue=coredata.get("prism:issueIdentifier"),
            pages=coredata.get("prism:pageRange"),
            source="sciencedirect",
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
        根据ID获取论文详情
        
        支持多种ID格式:
        - DOI: 10.1016/j.example.2023.01.001
        - PII: SXXXX-XXXX(23)00001-X
        - EID: 2-s2.0-XXXXXXXXX
        
        Args:
            paper_id: 论文ID
            
        Returns:
            Paper对象，不存在则返回None
            
        Raises:
            APIRequestError: API请求失败时抛出
        """
        params = {"httpAccept": "application/json"}
        
        # 尝试不同的ID格式
        if paper_id.startswith("10."):
            # DOI格式
            data = self._make_request(f"article/doi/{paper_id}", params)
        elif paper_id.startswith("pii:") or paper_id.startswith("S"):
            # PII格式
            pii = paper_id.replace("pii:", "")
            data = self._make_request(f"article/pii/{pii}", params)
        else:
            # 尝试EID
            if not paper_id.startswith("2-s2.0-"):
                paper_id = f"2-s2.0-{paper_id}"
            data = self._make_request(f"article/eid/{paper_id}", params)
        
        if not data or "full-text-retrieval-response" not in data:
            return None
        
        return self._parse_paper(data["full-text-retrieval-response"])
    
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
            page_size: 每页数量，默认20，最大100
            
        Returns:
            Paper对象列表
            
        Raises:
            APIRequestError: API请求失败时抛出
        """
        query = keyword
        if start_year and end_year:
            query += f" AND PUBYEAR > {start_year-1} AND PUBYEAR < {end_year+1}"
        elif start_year:
            query += f" AND PUBYEAR > {start_year-1}"
        elif end_year:
            query += f" AND PUBYEAR < {end_year+1}"
        
        params = {
            "query": query,
            "count": min(page_size, 100),
            "start": (page - 1) * page_size,
            "httpAccept": "application/json"
        }
        
        data = self._make_request("search/sciencedirect", params)
        entries = data.get("search-results", {}).get("entry", [])
        
        papers = []
        for entry in entries:
            papers.append(self._parse_search_result(entry))
        
        return papers
    
    def _parse_search_result(self, entry: Dict) -> Paper:
        """
        解析搜索结果条目为Paper对象
        
        Args:
            entry: 搜索结果条目
            
        Returns:
            Paper对象
        """
        # 获取URL
        url = None
        links = entry.get("link", [])
        if links:
            if isinstance(links, list):
                for link in links:
                    if isinstance(link, dict):
                        url = link.get("@href")
                        break
            elif isinstance(links, dict):
                url = links.get("@href")
        
        # 获取论文ID
        paper_id = entry.get("eid", "")
        if not paper_id:
            identifier = entry.get("dc:identifier", "")
            if identifier.startswith("doi:"):
                paper_id = identifier.replace("doi:", "")
            else:
                paper_id = identifier
        
        return Paper(
            paper_id=paper_id,
            title=entry.get("dc:title", ""),
            authors=[],  # 搜索结果不包含完整作者
            journal=entry.get("prism:publicationName", ""),
            publish_year=self._parse_year(entry.get("prism:coverDate", "")),
            publish_date=entry.get("prism:coverDate"),
            doi=entry.get("prism:doi"),
            url=url,
            source="sciencedirect",
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
        
        ScienceDirect不直接支持按作者ID搜索，需要使用作者姓名搜索。
        
        Args:
            author_id: 作者ID
            start_year: 开始年份（可选）
            end_year: 结束年份（可选）
            limit: 返回数量限制，默认100
            
        Returns:
            空列表（当前版本不支持）
        """
        logger.warning("ScienceDirect适配器不支持按作者ID获取论文，请使用作者姓名搜索")
        return []
    
    def get_author_info(self, author_id: str) -> Optional[Author]:
        """
        获取作者详细信息
        
        ScienceDirect不提供作者信息API。
        
        Args:
            author_id: 作者ID
            
        Returns:
            None（当前版本不支持）
        """
        logger.warning("ScienceDirect适配器不支持获取作者信息")
        return None
    
    def get_citation_relations(
        self, 
        paper_id: str, 
        depth: int = 1
    ) -> Dict[str, Any]:
        """
        获取论文的引证关系
        
        ScienceDirect不提供引证关系API。
        
        Args:
            paper_id: 论文ID
            depth: 引证关系深度
            
        Returns:
            空的引证关系字典
        """
        logger.warning("ScienceDirect适配器暂不支持引证关系获取")
        return {
            "paper_id": paper_id,
            "references": [],
            "citations": [],
            "citation_papers": [],
            "citation_count": 0
        }
    
    def get_journal_info(self, journal_id: str) -> Optional[Journal]:
        """
        获取期刊详细信息
        
        ScienceDirect不提供期刊信息API。
        
        Args:
            journal_id: 期刊ID
            
        Returns:
            None（当前版本不支持）
        """
        logger.warning("ScienceDirect适配器暂不支持期刊信息获取")
        return None
