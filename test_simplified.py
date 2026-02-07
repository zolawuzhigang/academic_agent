#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术Agent简化测试脚本
"""

from academic_agent.services import LocalAcademicService
from academic_agent.llm import get_llm_adapter
from academic_agent.qa import LLMEnhancedResearchModule
from academic_agent.config import load_config


def test_simplified():
    """简化版测试"""
    
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
    print("学术Agent功能测试（简化版）")
    print("=" * 80)
    
    # 问题1: 基础查询 - 搜索机器学习领域的最新论文
    print("\n" + "=" * 80)
    print("问题1: 2024年机器学习领域有哪些高被引论文？")
    print("=" * 80)
    
    try:
        results = service.search_papers(
            keyword="machine learning",
            start_year=2024,
            page_size=3
        )
        
        print(f"\n找到 {results['total']} 篇论文，以下是前3篇：\n")
        for i, paper in enumerate(results['papers'], 1):
            authors = [a.get('name', 'Unknown') if isinstance(a, dict) else str(a) 
                      for a in paper.get('authors', [])[:3]]
            print(f"{i}. {paper['title']}")
            print(f"   作者: {', '.join(authors)}")
            print(f"   被引: {paper.get('citations', 0)}")
            print(f"   期刊: {paper.get('journal', 'N/A')}")
            print(f"   年份: {paper.get('publish_year', 'N/A')}")
            print()
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 问题2: LLM增强 - 智能论文总结
    print("\n" + "=" * 80)
    print("问题2: 请总结Transformer相关的研究进展（使用LLM分析）")
    print("=" * 80)
    
    try:
        # 先搜索Transformer相关论文
        papers = service.search_papers(
            keyword="transformer architecture",
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
    
    # 问题3: 论文详情查询
    print("\n" + "=" * 80)
    print("问题3: 查询Attention Is All You Need这篇论文的详细信息")
    print("=" * 80)
    
    try:
        paper_id = "W2626778328"
        paper_info = service.get_paper_info(paper_id)
        
        if paper_info:
            print(f"\n论文标题: {paper_info.get('title', 'N/A')}")
            print(f"发表年份: {paper_info.get('publish_year', 'N/A')}")
            print(f"被引次数: {paper_info.get('citations', 0)}")
            print(f"期刊: {paper_info.get('journal', 'N/A')}")
            
            authors = [a.get('name', 'N/A') if isinstance(a, dict) else str(a) 
                      for a in paper_info.get('authors', [])[:5]]
            print(f"作者: {', '.join(authors)}")
            
            keywords = paper_info.get('keywords', [])
            if keywords:
                print(f"关键词: {', '.join(keywords[:5])}")
            
            abstract = paper_info.get('abstract', '')
            if abstract:
                print(f"\n摘要: {abstract[:300]}...")
        else:
            print("❌ 未找到该论文")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 问题4: LLM增强 - 研究趋势分析
    print("\n" + "=" * 80)
    print("问题4: 大语言模型领域的研究趋势是什么？（使用LLM分析）")
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
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    test_simplified()
