"""LLM模块初始化文件"""

from academic_agent.llm.base_llm import BaseLLMAdapter
from academic_agent.llm.openai_llm import OpenAILLMAdapter
from academic_agent.llm.anthropic_llm import AnthropicLLMAdapter
from academic_agent.llm.zhipu_llm import ZhipuLLMAdapter

__all__ = [
    "BaseLLMAdapter",
    "OpenAILLMAdapter",
    "AnthropicLLMAdapter",
    "ZhipuLLMAdapter",
    "get_llm_adapter"
]


def get_llm_adapter(provider: str, config: Dict[str, Any]) -> BaseLLMAdapter:
    """
    根据提供商名称获取LLM适配器
    
    Args:
        provider: 提供商名称 (openai/anthropic/zhipu)
        config: 配置字典
        
    Returns:
        LLM适配器实例
    """
    adapter_map = {
        "openai": OpenAILLMAdapter,
        "anthropic": AnthropicLLMAdapter,
        "zhipu": ZhipuLLMAdapter
    }
    
    if provider not in adapter_map:
        raise ValueError(
            f"不支持的LLM提供商: {provider}，"
            f"支持的提供商: {list(adapter_map.keys())}"
        )
    
    return adapter_map[provider](**config)
