"""数据清洗模块"""
import logging
import re
from typing import List, Optional, Dict, Any
from academic_agent.models import Paper, Author, Journal

logger = logging.getLogger(__name__)


class DataCleaner:
    """学术数据清洗器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化数据清洗器"""
        self.config = config or {}
        self.remove_duplicates = self.config.get("remove_duplicates", True)
        self.fill_missing = self.config.get("fill_missing", True)
        self.normalize_text = self.config.get("normalize_text", True)

    def clean_papers(self, papers: List[Paper]) -> List[Paper]:
        """清洗论文列表"""
        cleaned = []
        seen_ids = set()

        for paper in papers:
            if self.remove_duplicates:
                if paper.paper_id in seen_ids:
                    continue
                seen_ids.add(paper.paper_id)

            cleaned_paper = self.clean_paper(paper)
            if cleaned_paper:
                cleaned.append(cleaned_paper)

        return cleaned

    def clean_paper(self, paper: Paper) -> Optional[Paper]:
        """清洗单篇论文"""
        if not paper.paper_id or not paper.title:
            return None

        if self.normalize_text and paper.title:
            paper.title = self._normalize_text(paper.title)

        if self.normalize_text and paper.abstract:
            paper.abstract = self._normalize_text(paper.abstract)

        if paper.authors:
            paper.authors = [self.clean_author(a) for a in paper.authors if a]

        if paper.keywords:
            paper.keywords = [self._normalize_text(k) for k in paper.keywords if k]

        if self.fill_missing:
            paper = self._fill_paper_defaults(paper)

        return paper

    def clean_author(self, author: Author) -> Author:
        """清洗作者信息"""
        if self.normalize_text and author.name:
            author.name = self._normalize_text(author.name)
        if self.normalize_text and author.affiliation:
            author.affiliation = self._normalize_text(author.affiliation)
        return author

    def _normalize_text(self, text: str) -> str:
        """标准化文本"""
        if not text:
            return text
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
        return text

    def _fill_paper_defaults(self, paper: Paper) -> Paper:
        """填充论文默认值"""
        if paper.keywords is None:
            paper.keywords = []
        if paper.references is None:
            paper.references = []
        if paper.fields is None:
            paper.fields = []
        return paper

    def deduplicate_papers(self, papers: List[Paper], key_fields: List[str] = None) -> List[Paper]:
        """论文去重"""
        key_fields = key_fields or ["paper_id"]
        seen = set()
        unique = []

        for paper in papers:
            key_parts = []
            for field in key_fields:
                value = getattr(paper, field, None)
                if value:
                    key_parts.append(str(value).lower())

            key = "|".join(key_parts)
            if key not in seen:
                seen.add(key)
                unique.append(paper)

        return unique

    def filter_papers(self, papers: List[Paper], min_year: Optional[int] = None,
                      max_year: Optional[int] = None, min_citations: Optional[int] = None) -> List[Paper]:
        """过滤论文"""
        filtered = []

        for paper in papers:
            if min_year and paper.publish_year and paper.publish_year < min_year:
                continue
            if max_year and paper.publish_year and paper.publish_year > max_year:
                continue
            if min_citations and (paper.citations is None or paper.citations < min_citations):
                continue
            filtered.append(paper)

        return filtered
