"""
OpenAI LLM适配器

支持OpenAI GPT系列模型
"""

import requests
import logging
from typing import Dict, Any, List, Optional

from academic_agent.llm.base_llm import BaseLLMAdapter

logger = logging.getLogger(__name__)


class OpenAILLMAdapter(BaseLLMAdapter):
    """
    OpenAI LLM适配器
    
    支持GPT-4、GPT-3.5等模型
    
    Attributes:
        model_name: 模型名称 (gpt-4, gpt-3.5-turbo等)
        api_key: OpenAI API密钥
        base_url: API基础URL
    """
    
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        初始化OpenAI适配器
        
        Args:
            model_name: 模型名称
            api_key: OpenAI API密钥
            base_url: API基础URL（可选，默认使用官方API）
            temperature: 温度参数
            max_tokens: 最大token数
        """
        super().__init__(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url or self.DEFAULT_BASE_URL,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if not self.api_key:
            logger.warning("OpenAI API Key未配置")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天对话
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Returns:
            响应字典
        """
        if not self.api_key:
            raise ValueError("OpenAI API Key未配置")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens)
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            choice = result["choices"][0]
            
            return {
                "content": choice["message"]["content"],
                "usage": result.get("usage", {}),
                "model": result.get("model", self.model_name),
                "finish_reason": choice.get("finish_reason")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API请求失败: {e}")
            raise
    
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
            响应字典
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)
    
    @property
    def provider_name(self) -> str:
        """提供商名称"""
        return "OpenAI"
