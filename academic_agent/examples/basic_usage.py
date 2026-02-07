"""
基础使用示例
展示 Academic Agent 的基本功能使用
"""
from academic_agent import LocalAcademicService


def main():
    """主函数"""
    print("=" * 60)
    print("Academic Agent - 基础使用示例")
    print("=" * 60)
    
    # 初始化服务（使用OpenAlex适配器，免费开放API）
    print("\n[1] 初始化服务...")
    service = LocalAcademicService(adapter_name="openalex")
    print("✓ 服务初始化完成")
    
    # 搜索论文
    print("\n[2] 搜索论文...")
    print("-" * 40)
    results = service.search_papers(
        keyword="machine learning",
        start_year=2020,
        end_year=2024,
        page_size=5
    )
    print(f"找到 {results.get('total', 0)} 篇论文")
    print("\n前5篇论文:")
    for i, paper in enumerate(results.get("papers", []), 1):
        print(f"  {i}. {paper['title'][:80]}...")
        print(f"     年份: {paper.get('publish_year')}, 被引: {paper.get('citations_count', 0)}")
    
    # 获取作者信息
    print("\n[3] 获取作者信息...")
    print("-" * 40)
    # 使用一个示例作者ID（需要替换为实际存在的ID）
    author_id = "A5003442465"  # Yann LeCun
    author = service.get_author_info(author_id)
    if author:
        print(f"作者: {author['name']}")
        print(f"机构: {author.get('affiliation', 'N/A')}")
        print(f"H指数: {author.get('h_index', 'N/A')}")
        print(f"被引次数: {author.get('citations_count', 0)}")
        print(f"论文数量: {author.get('papers_count', 0)}")
    else:
        print(f"未找到作者信息 (ID: {author_id})")
    
    # 获取作者论文列表
    print("\n[4] 获取作者论文列表...")
    print("-" * 40)
    author_papers = service.get_author_papers(
        author_id=author_id,
        start_year=2020,
        end_year=2024,
        page_size=3
    )
    print(f"该作者 {author_papers.get('total', 0)} 篇论文 (2020-2024)")
    print("\n最近3篇:")
    for i, paper in enumerate(author_papers.get("papers", []), 1):
        print(f"  {i}. {paper['title'][:70]}...")
    
    # 获取年度发文统计
    print("\n[5] 获取作者年度发文统计...")
    print("-" * 40)
    stats = service.get_author_yearly_papers(
        author_id=author_id,
        start_year=2018,
        end_year=2023
    )
    print("年度发文量:")
    for year, count in sorted(stats.get("yearly_counts", {}).items()):
        bar = "█" * count
        print(f"  {year}: {bar} ({count})")
    
    # 获取作者合作网络
    print("\n[6] 获取作者合作网络...")
    print("-" * 40)
    network = service.get_author_cooperation_network(
        author_id=author_id,
        depth=1
    )
    print(f"合作网络统计:")
    print(f"  节点数: {network.get('total_nodes', 0)}")
    print(f"  边数: {network.get('total_edges', 0)}")
    print(f"\n主要合作者:")
    for node in network.get("nodes", [])[:5]:
        if node.get("id") != author_id:
            print(f"  - {node.get('name')} (合作{node.get('weight', 0)}次)")
    
    print("\n" + "=" * 60)
    print("示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
