"""
LLM适配器抽象基类

定义所有LLM适配器的统一接口规范
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseLLMAdapter(ABC):
    """
    LLM适配器抽象基类
    
    定义了所有LLM适配器必须实现的接口，支持多种LLM提供商。
    
    Attributes:
        model_name: 模型名称
        api_key: API密钥
        base_url: API基础URL
        temperature: 温度参数（控制随机性）
        max_tokens: 最大生成token数
    """
    
    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        初始化LLM适配器
        
        Args:
            model_name: 模型名称
            api_key: API密钥
            base_url: API基础URL
            temperature: 温度参数（0.0-2.0）
            max_tokens: 最大生成token数
        """
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天对话
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            **kwargs: 其他参数
            
        Returns:
            包含响应内容的字典:
            {
                "content": "回复内容",
                "usage": {"prompt_tokens": 10, "completion_tokens": 20},
                "model": "模型名称"
            }
        """
        pass
    
    @abstractmethod
    def complete(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        文本补全
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数
            
        Returns:
            包含响应内容的字典
        """
        pass
    
    def analyze_papers(
        self,
        papers: List[Dict[str, Any]],
        analysis_type: str = "summary"
    ) -> Dict[str, Any]:
        """
        分析论文列表
        
        Args:
            papers: 论文列表
            analysis_type: 分析类型 (summary/trend/gap/compare)
            
        Returns:
            分析结果
        """
        prompt = self._build_analysis_prompt(papers, analysis_type)
        result = self.complete(prompt)
        return {
            "analysis_type": analysis_type,
            "papers_count": len(papers),
            "result": result.get("content", ""),
            "model": self.model_name
        }
    
    def _build_analysis_prompt(
        self,
        papers: List[Dict[str, Any]],
        analysis_type: str
    ) -> str:
        """
        构建分析提示词
        
        Args:
            papers: 论文列表
            analysis_type: 分析类型
            
        Returns:
            提示词字符串
        """
        papers_text = "\n\n".join([
            f"论文{i+1}: {p.get('title', 'N/A')}\n"
            f"作者: {', '.join([a.get('name', 'Unknown') if isinstance(a, dict) else str(a) for a in p.get('authors', [])[:3]])}\n"
            f"摘要: {(p.get('abstract') or 'N/A')[:300]}..."
            for i, p in enumerate(papers[:5])
        ])
        
        prompts = {
            "summary": f"""请对以下论文进行总结分析：

{papers_text}

请提供：
1. 研究主题概述
2. 主要研究方法
3. 关键发现
4. 研究趋势""",
            
            "trend": f"""请分析以下论文的研究趋势：

{papers_text}

请提供：
1. 研究热点
2. 技术演进方向
3. 未来发展趋势""",
            
            "gap": f"""请识别以下论文中的研究空白：

{papers_text}

请提供：
1. 当前研究的局限性
2. 未解决的问题
3. 潜在的研究机会""",
            
            "compare": f"""请对比分析以下论文：

{papers_text}

请提供：
1. 各论文的优缺点
2. 方法对比
3. 适用场景分析"""
        }
        
        return prompts.get(analysis_type, prompts["summary"])
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """获取提供商名称"""
        pass
