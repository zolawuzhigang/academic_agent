#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试LLM配置是否正确
"""

from academic_agent.llm import get_llm_adapter
from academic_agent.qa import LLMEnhancedResearchModule
from academic_agent.services import LocalAcademicService
from academic_agent.config import load_config


def test_llm_config():
    """测试LLM配置"""
    print("=== 测试LLM配置 ===")
    
    # 加载配置
    config = load_config()
    llm_config = config.get("llm", {}).get("zhipu", {})
    
    # 1. 测试千问AI配置
    try:
        print("\n1. 测试千问AI配置...")
        print(f"   API Key: {llm_config.get('api_key', '')[:20]}...")
        print(f"   Base URL: {llm_config.get('base_url', '')}")
        print(f"   Model: {llm_config.get('model', '')}")
        
        llm_adapter = get_llm_adapter("zhipu", {
            "api_key": llm_config.get("api_key"),
            "model_name": llm_config.get("model", "qwen3-max"),
            "base_url": llm_config.get("base_url"),
            "temperature": llm_config.get("temperature", 0.7),
            "max_tokens": llm_config.get("max_tokens", 2000)
        })
        
        # 测试简单对话
        response = llm_adapter.complete("你好，请问你是谁？")
        print("✅ 千问AI配置成功！")
        print(f"   模型响应: {response.get('content', '').strip()[:100]}...")
        
    except Exception as e:
        print(f"❌ 千问AI配置失败: {e}")
    
    # 2. 测试学术服务
    try:
        print("\n2. 测试学术服务...")
        service = LocalAcademicService(adapter_name="openalex")
        
        # 测试论文搜索
        results = service.search_papers("machine learning", start_year=2023, page_size=2)
        print("✅ 学术服务配置成功！")
        print(f"   找到 {results['total']} 篇论文")
        for i, paper in enumerate(results['papers'], 1):
            print(f"   {i}. {paper['title']}")
            # 处理作者信息（authors是字典列表）
            authors = []
            for author in paper['authors'][:3]:
                if isinstance(author, dict):
                    authors.append(author.get('name', 'Unknown'))
                else:
                    authors.append(str(author))
            print(f"   作者: {', '.join(authors)}")
            print(f"   被引: {paper.get('citations', 0)}")
            print(f"   年份: {paper.get('publish_year', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ 学术服务配置失败: {e}")
    
    # 3. 测试LLM增强功能
    try:
        print("\n3. 测试LLM增强功能...")
        llm_adapter = get_llm_adapter("zhipu", {
            "api_key": llm_config.get("api_key"),
            "model_name": llm_config.get("model", "qwen3-max"),
            "base_url": llm_config.get("base_url"),
            "temperature": llm_config.get("temperature", 0.7),
            "max_tokens": llm_config.get("max_tokens", 2000)
        })
        
        service = LocalAcademicService(adapter_name="openalex")
        llm_module = LLMEnhancedResearchModule(
            adapter=service.adapter,
            llm_adapter=llm_adapter
        )
        
        # 测试智能论文总结
        result = llm_module.handle({
            "type": "smart_summary",
            "paper_ids": ["W2741809807"]  # Attention Is All You Need
        })
        
        if result.get('code') == 200:
            print("✅ LLM增强功能配置成功！")
            summary = result['data'].get('summary', '')
            print(f"   论文总结: {summary[:200]}...")
        else:
            print(f"❌ LLM增强功能失败: {result.get('msg', '未知错误')}")
        
    except Exception as e:
        print(f"❌ LLM增强功能配置失败: {e}")


if __name__ == "__main__":
    test_llm_config()
