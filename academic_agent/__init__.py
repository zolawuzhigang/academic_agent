"""
学术Agent - 低耦合、可插拔的学术研究助手

支持对接Scopus、ScienceDirect、OpenAlex等学术API，
提供从基础查询到深度分析的全场景学术研究问答能力。

主要功能:
    - 论文搜索与获取
    - 作者信息查询
    - 期刊指标分析
    - 引证关系分析
    - 统计分析
    - 深度研究分析
    - LLM增强的智能分析

Example:
    >>> from academic_agent import LocalAcademicService
    >>> from academic_agent.llm import get_llm_adapter
    >>> from academic_agent.qa import LLMEnhancedResearchModule
    >>> 
    >>> # 创建服务
    >>> service = LocalAcademicService(adapter_name="openalex")
    >>> 
    >>> # 创建LLM适配器
    >>> llm = get_llm_adapter("zhipu", {"api_key": "your_key"})
    >>> 
    >>> # 创建LLM增强模块
    >>> llm_module = LLMEnhancedResearchModule(service.adapter, llm)
    >>> 
    >>> # 使用LLM分析
    >>> result = llm_module.handle({"type": "smart_summary", "paper_ids": [...]})
"""

__version__ = "1.0.0"
__author__ = "Academic Agent Team"

# 导出核心类
from academic_agent.models import Paper, Author, Journal
from academic_agent.adapters import BaseAcademicAdapter
from academic_agent.qa import BaseQAModule
from academic_agent.services import LocalAcademicService, create_app, start_server

# 导出LLM相关类
from academic_agent.llm import BaseLLMAdapter, get_llm_adapter
from academic_agent.qa import LLMEnhancedResearchModule

__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    # 数据模型
    "Paper",
    "Author",
    "Journal",
    # 抽象基类
    "BaseAcademicAdapter",
    "BaseQAModule",
    "BaseLLMAdapter",
    # 服务
    "LocalAcademicService",
    "create_app",
    "start_server",
    # LLM
    "get_llm_adapter",
    "LLMEnhancedResearchModule"
]
