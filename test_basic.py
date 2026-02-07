#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术Agent基础功能测试
"""

from academic_agent.services import LocalAcademicService


def test_basic_functions():
    """测试基础功能"""
    
    service = LocalAcademicService(adapter_name="openalex")
    
    print("=" * 80)
    print("学术Agent基础功能测试")
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
    
    # 问题2: 论文详情查询
    print("\n" + "=" * 80)
    print("问题2: 查询Attention Is All You Need这篇论文的详细信息")
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
    
    # 问题3: 搜索深度学习相关论文
    print("\n" + "=" * 80)
    print("问题3: 深度学习领域有哪些重要论文？")
    print("=" * 80)
    
    try:
        results = service.search_papers(
            keyword="deep learning",
            start_year=2023,
            page_size=3
        )
        
        print(f"\n找到 {results['total']} 篇论文，以下是前3篇：\n")
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
    
    # 问题4: 搜索大语言模型相关论文
    print("\n" + "=" * 80)
    print("问题4: 大语言模型领域有哪些最新研究？")
    print("=" * 80)
    
    try:
        results = service.search_papers(
            keyword="large language model",
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
            print(f"   年份: {paper.get('publish_year', 'N/A')}")
            print()
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 问题5: 搜索GPT相关论文
    print("\n" + "=" * 80)
    print("问题5: GPT相关的研究有哪些？")
    print("=" * 80)
    
    try:
        results = service.search_papers(
            keyword="GPT",
            start_year=2023,
            page_size=3
        )
        
        print(f"\n找到 {results['total']} 篇论文，以下是前3篇：\n")
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
    
    print("\n" + "=" * 80)
    print("基础功能测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    test_basic_functions()
