#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索Attention Is All You Need的正确ID
"""

from academic_agent.services import LocalAcademicService


def find_attention_paper():
    """搜索Attention Is All You Need论文"""
    
    service = LocalAcademicService(adapter_name="openalex")
    
    print("搜索Attention Is All You Need论文...")
    results = service.search_papers(
        keyword="Attention Is All You Need",
        page_size=5
    )
    
    print(f"\n找到 {results['total']} 篇相关论文：\n")
    
    for i, paper in enumerate(results['papers'], 1):
        authors = [a.get('name', 'Unknown') if isinstance(a, dict) else str(a) 
                  for a in paper.get('authors', [])[:3]]
        print(f"{i}. {paper['title']}")
        print(f"   论文ID: {paper['paper_id']}")
        print(f"   作者: {', '.join(authors)}")
        print(f"   被引: {paper.get('citations', 0)}")
        print(f"   年份: {paper.get('publish_year', 'N/A')}")
        print(f"   期刊: {paper.get('journal', 'N/A')}")
        print()


if __name__ == "__main__":
    find_attention_paper()
