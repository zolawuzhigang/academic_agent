"""
智谱AI LLM适配器

支持智谱AI GLM系列模型
"""

import requests
import logging
from typing import Dict, Any, List, Optional

from academic_agent.llm.base_llm import BaseLLMAdapter

logger = logging.getLogger(__name__)


class ZhipuLLMAdapter(BaseLLMAdapter):
    """
    智谱AI LLM适配器
    
    支持GLM-4、GLM-3-Turbo等模型
    
    Attributes:
        model_name: 模型名称 (glm-4, glm-3-turbo等)
        api_key: 智谱AI API密钥
        base_url: API基础URL
    """
    
    DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
    
    def __init__(
        self,
        model_name: str = "glm-4",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        初始化智谱AI适配器
        
        Args:
            model_name: 模型名称
            api_key: 智谱AI API密钥
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
            logger.warning("智谱AI API Key未配置")
    
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
            raise ValueError("智谱AI API Key未配置")
        
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
            # 检查base_url是否已经包含了完整路径
            if self.base_url.endswith("/chat/completions"):
                url = self.base_url
            else:
                url = f"{self.base_url}/chat/completions"
            
            response = requests.post(
                url,
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
            logger.error(f"智谱AI API请求失败: {e}")
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
        return "智谱AI"
