"""
数据导出示例
展示如何导出学术数据为不同格式
"""
from academic_agent import LocalAcademicService
from academic_agent.processors import DataConverter
import json
import os


def export_to_json(service, keyword, output_file):
    """导出为JSON格式"""
    print(f"\n[导出为JSON] {output_file}")
    print("-" * 40)
    
    # 搜索论文
    results = service.search_papers(keyword, page_size=10)
    papers = results.get("papers", [])
    
    # 转换为JSON
    converter = DataConverter()
    json_data = converter.to_json(papers)
    
    # 保存文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(json_data)
    
    print(f"✓ 导出成功: {len(papers)} 篇论文")
    print(f"✓ 文件大小: {os.path.getsize(output_file)} bytes")
    print(f"✓ 保存路径: {output_file}")
    
    return output_file


def export_to_csv(service, keyword, output_file):
    """导出为CSV格式"""
    print(f"\n[导出为CSV] {output_file}")
    print("-" * 40)
    
    # 搜索论文
    results = service.search_papers(keyword, page_size=10)
    papers = results.get("papers", [])
    
    # 转换为CSV
    converter = DataConverter()
    csv_data = converter.to_csv(papers)
    
    # 保存文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(csv_data)
    
    print(f"✓ 导出成功: {len(papers)} 篇论文")
    print(f"✓ 文件大小: {os.path.getsize(output_file)} bytes")
    print(f"✓ 保存路径: {output_file}")
    
    # 显示CSV内容预览
    print("\nCSV预览 (前3行):")
    lines = csv_data.strip().split('\n')[:4]
    for line in lines:
        print(f"  {line[:100]}...")
    
    return output_file


def export_to_bibtex(service, keyword, output_file):
    """导出为BibTeX格式"""
    print(f"\n[导出为BibTeX] {output_file}")
    print("-" * 40)
    
    # 搜索论文
    results = service.search_papers(keyword, page_size=5)
    papers = results.get("papers", [])
    
    # 转换为BibTeX
    converter = DataConverter()
    bibtex_data = converter.to_bibtex(papers)
    
    # 保存文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(bibtex_data)
    
    print(f"✓ 导出成功: {len(papers)} 篇论文")
    print(f"✓ 文件大小: {os.path.getsize(output_file)} bytes")
    print(f"✓ 保存路径: {output_file}")
    
    # 显示BibTeX内容预览
    print("\nBibTeX预览:")
    entries = bibtex_data.split('\n\n')[:2]
    for entry in entries:
        for line in entry.split('\n')[:5]:
            print(f"  {line}")
        print("  ...")
    
    return output_file


def export_author_papers(service, author_id, output_dir):
    """导出作者的所有论文"""
    print(f"\n[导出作者论文] 作者ID: {author_id}")
    print("-" * 40)
    
    # 获取作者信息
    author = service.get_author_info(author_id)
    if not author:
        print(f"✗ 未找到作者 (ID: {author_id})")
        return
    
    print(f"作者: {author.get('name')}")
    
    # 获取作者论文
    results = service.get_author_papers(author_id, page_size=20)
    papers = results.get("papers", [])
    
    print(f"论文数量: {len(papers)}")
    
    # 导出为多种格式
    converter = DataConverter()
    
    # JSON格式
    json_file = os.path.join(output_dir, f"{author_id}_papers.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(converter.to_json(papers))
    print(f"✓ JSON: {json_file}")
    
    # CSV格式
    csv_file = os.path.join(output_dir, f"{author_id}_papers.csv")
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(converter.to_csv(papers))
    print(f"✓ CSV: {csv_file}")
    
    # BibTeX格式
    bibtex_file = os.path.join(output_dir, f"{author_id}_papers.bib")
    with open(bibtex_file, 'w', encoding='utf-8') as f:
        f.write(converter.to_bibtex(papers))
    print(f"✓ BibTeX: {bibtex_file}")


def export_analysis_results(service, keyword, output_dir):
    """导出分析结果"""
    print(f"\n[导出分析结果] 关键词: {keyword}")
    print("-" * 40)
    
    # 研究趋势
    print("\n1. 研究趋势分析...")
    trend = service.get_research_trend(keyword, time_window=5)
    trend_file = os.path.join(output_dir, f"{keyword.replace(' ', '_')}_trend.json")
    with open(trend_file, 'w', encoding='utf-8') as f:
        json.dump(trend, f, indent=2, ensure_ascii=False)
    print(f"✓ 趋势分析: {trend_file}")
    
    # 高被引论文
    print("\n2. 高被引论文...")
    top_cited = service.get_top_cited_papers(keyword, 2019, 2024, top_n=10)
    top_cited_file = os.path.join(output_dir, f"{keyword.replace(' ', '_')}_top_cited.json")
    with open(top_cited_file, 'w', encoding='utf-8') as f:
        json.dump(top_cited, f, indent=2, ensure_ascii=False)
    print(f"✓ 高被引论文: {top_cited_file}")
    
    # 关键词共现
    print("\n3. 关键词共现分析...")
    cooccurrence = service.get_keyword_cooccurrence(keyword, 2020, 2024, top_n=20)
    cooccurrence_file = os.path.join(output_dir, f"{keyword.replace(' ', '_')}_cooccurrence.json")
    with open(cooccurrence_file, 'w', encoding='utf-8') as f:
        json.dump(cooccurrence, f, indent=2, ensure_ascii=False)
    print(f"✓ 关键词共现: {cooccurrence_file}")


def batch_export(service, keywords, output_dir):
    """批量导出多个关键词的数据"""
    print(f"\n[批量导出] {len(keywords)} 个关键词")
    print("-" * 40)
    
    for keyword in keywords:
        print(f"\n处理: {keyword}")
        
        # 创建子目录
        keyword_dir = os.path.join(output_dir, keyword.replace(' ', '_'))
        os.makedirs(keyword_dir, exist_ok=True)
        
        # 导出论文数据
        results = service.search_papers(keyword, page_size=20)
        papers = results.get("papers", [])
        
        converter = DataConverter()
        
        # JSON
        json_file = os.path.join(keyword_dir, "papers.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(converter.to_json(papers))
        
        # CSV
        csv_file = os.path.join(keyword_dir, "papers.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(converter.to_csv(papers))
        
        print(f"  ✓ 导出 {len(papers)} 篇论文")


def main():
    """主函数"""
    print("=" * 60)
    print("Academic Agent - 数据导出示例")
    print("=" * 60)
    
    # 创建输出目录
    output_dir = "./export_output"
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n输出目录: {output_dir}")
    
    # 初始化服务
    print("\n[初始化服务]")
    service = LocalAcademicService(adapter_name="openalex")
    print("✓ 服务初始化完成")
    
    # 导出为JSON
    export_to_json(
        service, 
        "machine learning", 
        os.path.join(output_dir, "ml_papers.json")
    )
    
    # 导出为CSV
    export_to_csv(
        service, 
        "deep learning", 
        os.path.join(output_dir, "dl_papers.csv")
    )
    
    # 导出为BibTeX
    export_to_bibtex(
        service, 
        "neural networks", 
        os.path.join(output_dir, "nn_papers.bib")
    )
    
    # 导出作者论文
    export_author_papers(
        service,
        "A5003442465",  # Yann LeCun
        output_dir
    )
    
    # 导出分析结果
    export_analysis_results(
        service,
        "artificial intelligence",
        output_dir
    )
    
    # 批量导出
    keywords = ["computer vision", "natural language processing", "reinforcement learning"]
    batch_export(service, keywords, output_dir)
    
    print("\n" + "=" * 60)
    print("数据导出示例运行完成!")
    print(f"导出文件保存在: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
