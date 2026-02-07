"""
Anthropic LLM适配器

支持Anthropic Claude系列模型
"""

import requests
import logging
from typing import Dict, Any, List, Optional

from academic_agent.llm.base_llm import BaseLLMAdapter

logger = logging.getLogger(__name__)


class AnthropicLLMAdapter(BaseLLMAdapter):
    """
    Anthropic LLM适配器
    
    支持Claude-3、Claude-2等模型
    
    Attributes:
        model_name: 模型名称 (claude-3-opus, claude-3-sonnet等)
        api_key: Anthropic API密钥
        base_url: API基础URL
    """
    
    DEFAULT_BASE_URL = "https://api.anthropic.com/v1"
    
    def __init__(
        self,
        model_name: str = "claude-3-sonnet-20240229",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        初始化Anthropic适配器
        
        Args:
            model_name: 模型名称
            api_key: Anthropic API密钥
            base_url: API基础URL（可选）
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
            logger.warning("Anthropic API Key未配置")
    
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
            raise ValueError("Anthropic API Key未配置")
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
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
                f"{self.base_url}/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "content": result["content"][0]["text"],
                "usage": result.get("usage", {}),
                "model": result.get("model", self.model_name),
                "stop_reason": result.get("stop_reason")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Anthropic API请求失败: {e}")
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
        return "Anthropic"
