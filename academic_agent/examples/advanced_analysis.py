"""
高级分析示例
展示 Academic Agent 的高级分析功能
"""
from academic_agent import LocalAcademicService
import json


def print_json(data, indent=2):
    """打印格式化的JSON"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def main():
    """主函数"""
    print("=" * 60)
    print("Academic Agent - 高级分析示例")
    print("=" * 60)
    
    # 初始化服务
    print("\n[1] 初始化服务...")
    service = LocalAcademicService(adapter_name="openalex")
    print("✓ 服务初始化完成")
    
    # 研究方向趋势分析
    print("\n[2] 研究方向趋势分析...")
    print("-" * 40)
    trend = service.get_research_trend(
        field="artificial intelligence",
        time_window=5
    )
    print(f"研究领域: {trend.get('field')}")
    print(f"分析时段: {trend.get('period')}")
    print(f"\n年度趋势:")
    for year, data in sorted(trend.get('yearly_trend', {}).items()):
        print(f"  {year}: {data.get('paper_count')} 篇论文, "
              f"{data.get('citation_count')} 次被引")
    
    print(f"\n新兴研究主题:")
    for topic in trend.get('emerging_topics', [])[:5]:
        print(f"  - {topic}")
    
    print(f"\n研究热点关键词:")
    for keyword in trend.get('hot_keywords', [])[:5]:
        print(f"  - {keyword}")
    
    # 研究空白识别
    print("\n[3] 研究空白识别...")
    print("-" * 40)
    gaps = service.get_research_gaps(
        field="machine learning",
        sub_field="federated learning"
    )
    print(f"研究领域: {gaps.get('field')}")
    print(f"子领域: {gaps.get('sub_field')}")
    print(f"\n潜在研究空白:")
    for gap in gaps.get('potential_research_gaps', []):
        print(f"  - {gap}")
    
    print(f"\n建议研究方向:")
    for direction in gaps.get('suggested_directions', []):
        print(f"  - {direction}")
    
    # 关键词共现分析
    print("\n[4] 关键词共现分析...")
    print("-" * 40)
    cooccurrence = service.get_keyword_cooccurrence(
        keyword="deep learning",
        start_year=2020,
        end_year=2024,
        top_n=10
    )
    print(f"核心关键词: {cooccurrence.get('keyword')}")
    print(f"\n共现关键词:")
    for kw, count in cooccurrence.get('cooccurrence', {}).items():
        bar = "█" * min(count, 20)
        print(f"  {kw}: {bar} ({count})")
    
    # 引证关系分析
    print("\n[5] 引证关系分析...")
    print("-" * 40)
    # 使用一个示例论文ID
    paper_id = "W2741809807"  # Attention Is All You Need
    citation = service.get_citation_relations(
        paper_id=paper_id,
        direction="both"
    )
    print(f"论文ID: {citation.get('paper_id')}")
    print(f"被引论文数: {len(citation.get('cited_by', []))}")
    print(f"引用论文数: {len(citation.get('citing', []))}")
    
    print(f"\n被引论文示例 (前3篇):")
    for paper in citation.get('cited_by', [])[:3]:
        print(f"  - {paper.get('title', 'N/A')[:60]}...")
        print(f"    作者: {', '.join(paper.get('authors', [])[:3])}")
    
    # 跨领域研究关联
    print("\n[6] 跨领域研究关联挖掘...")
    print("-" * 40)
    cross_field = service.get_cross_field_analysis(
        field1="computer vision",
        field2="natural language processing",
        time_window=3
    )
    print(f"领域1: {cross_field.get('field1')}")
    print(f"领域2: {cross_field.get('field2')}")
    print(f"\n交叉研究论文数: {cross_field.get('cross_papers_count', 0)}")
    print(f"\n共同关键词:")
    for kw in cross_field.get('common_keywords', [])[:5]:
        print(f"  - {kw}")
    
    # 高被引论文TopN
    print("\n[7] 高被引论文TopN...")
    print("-" * 40)
    top_cited = service.get_top_cited_papers(
        keyword="transformer",
        start_year=2017,
        end_year=2024,
        top_n=5
    )
    print(f"关键词: {top_cited.get('keyword')}")
    print(f"\nTop 5 高被引论文:")
    for i, paper in enumerate(top_cited.get('papers', []), 1):
        print(f"  {i}. {paper.get('title', 'N/A')[:60]}...")
        print(f"     被引次数: {paper.get('citations_count', 0)}")
        print(f"     作者: {', '.join(paper.get('authors', [])[:3])}")
    
    print("\n" + "=" * 60)
    print("高级分析示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
