"""问答模块"""

from academic_agent.qa.base_qa import BaseQAModule
from academic_agent.qa.basic_query import BasicQueryModule
from academic_agent.qa.statistical_analysis import StatisticalAnalysisModule
from academic_agent.qa.relation_analysis import RelationAnalysisModule
from academic_agent.qa.deep_research import DeepResearchModule
from academic_agent.qa.custom_output import CustomOutputModule
from academic_agent.qa.llm_enhanced import LLMEnhancedResearchModule

__all__ = [
    "BaseQAModule",
    "BasicQueryModule",
    "StatisticalAnalysisModule",
    "RelationAnalysisModule",
    "DeepResearchModule",
    "CustomOutputModule",
    "LLMEnhancedResearchModule"
]
