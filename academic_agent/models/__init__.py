"""
学术Agent数据模型模块

提供论文、作者、期刊等核心数据模型的定义
"""

from academic_agent.models.paper import Paper
from academic_agent.models.author import Author
from academic_agent.models.journal import Journal

__all__ = ["Paper", "Author", "Journal"]
