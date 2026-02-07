"""格式化工具"""
import re
from typing import Any, List, Optional


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """截断文本"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + suffix


def format_number(num: Any, decimal_places: int = 2) -> str:
    """格式化数字"""
    if num is None:
        return "N/A"
    try:
        return f"{float(num):.{decimal_places}f}"
    except (ValueError, TypeError):
        return str(num)


def slugify(text: str) -> str:
    """将文本转换为URL友好的格式"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def format_author_name(name: str) -> str:
    """格式化作者姓名"""
    if not name:
        return ""
    parts = name.split()
    if len(parts) > 1:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"
    return name


def format_date(date_str: str, input_format: str = "%Y-%m-%d", output_format: str = "%Y") -> str:
    """格式化日期"""
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, input_format)
        return dt.strftime(output_format)
    except ValueError:
        return date_str


def normalize_string(text: str) -> str:
    """标准化字符串"""
    if not text:
        return text
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def extract_year(date_str: str) -> Optional[int]:
    """从日期字符串中提取年份"""
    if not date_str:
        return None
    match = re.search(r'\b(19|20)\d{2}\b', date_str)
    if match:
        return int(match.group())
    return None


def format_list(items: List[str], separator: str = ", ") -> str:
    """格式化列表"""
    if not items:
        return ""
    return separator.join(str(item) for item in items if item)


def clean_doi(doi: str) -> str:
    """清理DOI"""
    if not doi:
        return doi
    doi = doi.strip()
    doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)
    return doi
