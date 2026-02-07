#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术Agent测试脚本 - 用学术问题测试agent功能
"""

from academic_agent.services import LocalAcademicService
from academic_agent.llm import get_llm_adapter
from academic_agent.qa import LLMEnhancedResearchModule
from academic_agent.config import load_config


def test_academic_questions():
    """用学术问题测试agent"""
    
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
    print("学术Agent功能测试")
    print("=" * 80)
    
    # 问题1: 基础查询 - 搜索机器学习领域的最新论文
    print("\n" + "=" * 80)
    print("问题1: 2024年机器学习领域有哪些高被引论文？")
    print("=" * 80)
    
    try:
        results = service.search_papers(
            keyword="machine learning",
            start_year=2024,
            page_size=5
        )
        
        print(f"\n找到 {results['total']} 篇论文，以下是前5篇：\n")
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
    
    # 问题2: 作者分析 - 查询著名AI研究者的论文
    print("\n" + "=" * 80)
    print("问题2: Geoffrey Hinton最近的研究方向是什么？")
    print("=" * 80)
    
    try:
        # 先搜索Geoffrey Hinton的论文
        results = service.search_papers(
            keyword="Geoffrey Hinton",
            start_year=2020,
            page_size=3
        )
        
        print(f"\n找到 {results['total']} 篇相关论文：\n")
        for i, paper in enumerate(results['papers'], 1):
            authors = [a.get('name', 'Unknown') if isinstance(a, dict) else str(a) 
                      for a in paper.get('authors', [])[:3]]
            print(f"{i}. {paper['title']}")
            print(f"   作者: {', '.join(authors)}")
            print(f"   被引: {paper.get('citations', 0)}")
            print(f"   年份: {paper.get('publish_year', 'N/A')}")
            print()
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 问题3: 统计分析 - 深度学习领域的年度发表趋势
    print("\n" + "=" * 80)
    print("问题3: 深度学习领域近5年的发表趋势如何？")
    print("=" * 80)
    
    try:
        stats = service.get_keyword_yearly_stats(
            keyword="deep learning",
            start_year=2019,
            end_year=2023
        )
        
        print("\n年度发表统计：\n")
        if stats.get('yearly_stats'):
            for year_stat in stats['yearly_stats']:
                print(f"  {year_stat.get('year', 'N/A')}: {year_stat.get('count', 0)} 篇")
        else:
            print("  暂无统计数据")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 问题4: LLM增强 - 智能论文总结
    print("\n" + "=" * 80)
    print("问题4: 请总结Transformer相关的研究进展（使用LLM分析）")
    print("=" * 80)
    
    try:
        # 先搜索Transformer相关论文
        papers = service.search_papers(
            keyword="transformer architecture",
            start_year=2022,
            page_size=3
        )
        
        if papers['papers']:
            # 使用LLM进行智能总结
            result = llm_module.handle({
                "type": "smart_summary",
                "paper_ids": [p['paper_id'] for p in papers['papers']]
            })
            
            if result.get('code') == 200:
                print(f"\n📊 论文数量: {result['data'].get('papers_count', 0)}")
                print(f"🤖 分析模型: {result['data'].get('model', 'N/A')}")
                print(f"\n📝 智能总结:\n")
                print(result['data'].get('summary', '暂无总结'))
            else:
                print(f"❌ LLM分析失败: {result.get('msg', '未知错误')}")
        else:
            print("❌ 未找到相关论文")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 问题5: LLM增强 - 研究趋势分析
    print("\n" + "=" * 80)
    print("问题5: 大语言模型领域的研究趋势是什么？（使用LLM分析）")
    print("=" * 80)
    
    try:
        result = llm_module.handle({
            "type": "research_trend_analysis",
            "keyword": "large language model",
            "start_year": 2022,
            "end_year": 2024
        })
        
        if result.get('code') == 200:
            print(f"\n📊 分析时间范围: {result['data'].get('period', 'N/A')}")
            print(f"📄 论文数量: {result['data'].get('papers_count', 0)}")
            print(f"🤖 分析模型: {result['data'].get('model', 'N/A')}")
            print(f"\n📈 趋势分析:\n")
            print(result['data'].get('trend_analysis', '暂无分析'))
        else:
            print(f"❌ LLM分析失败: {result.get('msg', '未知错误')}")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 问题6: 关联分析 - 论文引证关系
    print("\n" + "=" * 80)
    print("问题6: Attention Is All You Need这篇论文的引证关系如何？")
    print("=" * 80)
    
    try:
        # Attention Is All You Need的OpenAlex ID
        paper_id = "W2626778328"
        
        # 获取论文详情
        paper_info = service.get_paper_info(paper_id)
        if paper_info:
            print(f"\n论文标题: {paper_info.get('title', 'N/A')}")
            print(f"发表年份: {paper_info.get('publish_year', 'N/A')}")
            print(f"被引次数: {paper_info.get('citations', 0)}")
            print(f"作者: {', '.join([a.get('name', 'N/A') if isinstance(a, dict) else str(a) 
                                   for a in paper_info.get('authors', [])[:3]])}")
            print()
        
        # 获取引证关系
        citation_data = service.get_citation_relations(paper_id, depth=1)
        
        print(f"引用该论文的数量: {citation_data.get('citation_count', 0)}")
        print(f"\n引用该论文的前5篇论文：\n")
        
        citing_papers = citation_data.get('citation_papers', [])[:5]
        for i, paper in enumerate(citing_papers, 1):
            authors = [a.get('name', 'Unknown') if isinstance(a, dict) else str(a) 
                      for a in paper.authors[:3]]
            print(f"{i}. {paper.title}")
            print(f"   作者: {', '.join(authors)}")
            print(f"   被引: {paper.citations}")
            print()
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    test_academic_questions()
