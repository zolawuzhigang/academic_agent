#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术Agent LLM增强功能测试
"""

from academic_agent.services import LocalAcademicService
from academic_agent.llm import get_llm_adapter
from academic_agent.qa import LLMEnhancedResearchModule
from academic_agent.config import load_config


def test_llm_features():
    """测试LLM增强功能"""
    
    # 加载配置
    config = load_config()
    llm_config = config.get("llm", {}).get("zhipu", {})
    
    # 初始化服务
    service = LocalAcademicService(adapter_name="openalex")
    
    # 初始化LLM
    llm_adapter = get_llm_adapter("zhipu", {
        "api_key": llm_config.get("api_key"),
        "model_name": llm_config.get("model", "qwen3-max"),
        "base_url": llm_config.get("base_url"),
        "temperature": llm_config.get("temperature", 0.7),
        "max_tokens": llm_config.get("max_tokens", 2000)
    })
    
    # 初始化LLM增强模块
    llm_module = LLMEnhancedResearchModule(
        adapter=service.adapter,
        llm_adapter=llm_adapter
    )
    
    print("=" * 80)
    print("学术Agent LLM增强功能测试")
    print("=" * 80)
    
    # 问题1: LLM增强 - 智能论文总结
    print("\n" + "=" * 80)
    print("问题1: 请总结GPT-4相关的研究（使用LLM分析）")
    print("=" * 80)
    
    try:
        # 先搜索GPT-4相关论文
        papers = service.search_papers(
            keyword="GPT-4",
            start_year=2023,
            page_size=2
        )
        
        if papers['papers']:
            print(f"\n找到 {len(papers['papers'])} 篇论文，正在使用LLM进行分析...\n")
            
            # 使用LLM进行智能总结
            result = llm_module.handle({
                "type": "smart_summary",
                "paper_ids": [p['paper_id'] for p in papers['papers']]
            })
            
            if result.get('code') == 200:
                print(f"📊 论文数量: {result['data'].get('papers_count', 0)}")
                print(f"🤖 分析模型: {result['data'].get('model', 'N/A')}")
                print(f"\n📝 智能总结:\n")
                print(result['data'].get('summary', '暂无总结'))
            else:
                print(f"❌ LLM分析失败: {result.get('msg', '未知错误')}")
        else:
            print("❌ 未找到相关论文")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 问题2: LLM增强 - 研究趋势分析
    print("\n" + "=" * 80)
    print("问题2: 大语言模型领域的研究趋势是什么？（使用LLM分析）")
    print("=" * 80)
    
    try:
        print(f"\n正在搜索大语言模型相关论文并使用LLM进行分析...\n")
        
        result = llm_module.handle({
            "type": "research_trend_analysis",
            "keyword": "large language model",
            "start_year": 2023,
            "end_year": 2024
        })
        
        if result.get('code') == 200:
            print(f"📊 分析时间范围: {result['data'].get('period', 'N/A')}")
            print(f"📄 论文数量: {result['data'].get('papers_count', 0)}")
            print(f"🤖 分析模型: {result['data'].get('model', 'N/A')}")
            print(f"\n📈 趋势分析:\n")
            print(result['data'].get('trend_analysis', '暂无分析'))
        else:
            print(f"❌ LLM分析失败: {result.get('msg', '未知错误')}")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    print("\n" + "=" * 80)
    print("LLM增强功能测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    test_llm_features()
