"""
适配器切换示例
展示如何在不同API适配器之间切换
"""
from academic_agent import LocalAcademicService


def compare_adapters(keyword="machine learning", page_size=3):
    """比较不同适配器的搜索结果"""
    print("=" * 60)
    print("适配器切换示例 - 比较不同API的搜索结果")
    print("=" * 60)
    
    adapters = ["openalex"]  # 默认使用OpenAlex（免费开放）
    
    # 如果有其他API的密钥，可以取消注释
    # adapters = ["openalex", "scopus", "sciencedirect"]
    
    results_comparison = {}
    
    for adapter_name in adapters:
        print(f"\n{'='*60}")
        print(f"使用适配器: {adapter_name.upper()}")
        print("=" * 60)
        
        try:
            # 初始化服务
            service = LocalAcademicService(adapter_name=adapter_name)
            print(f"✓ {adapter_name} 适配器初始化成功")
            
            # 搜索论文
            results = service.search_papers(
                keyword=keyword,
                start_year=2020,
                end_year=2024,
                page_size=page_size
            )
            
            results_comparison[adapter_name] = {
                "total": results.get("total", 0),
                "papers": results.get("papers", [])
            }
            
            print(f"\n找到 {results.get('total', 0)} 篇论文")
            print(f"\n前{page_size}篇论文:")
            for i, paper in enumerate(results.get("papers", []), 1):
                print(f"  {i}. {paper['title'][:70]}...")
                print(f"     年份: {paper.get('publish_year')}")
                print(f"     被引: {paper.get('citations_count', 0)}")
                print(f"     作者: {', '.join(paper.get('authors', [])[:3])}")
                
        except Exception as e:
            print(f"✗ {adapter_name} 适配器错误: {e}")
            results_comparison[adapter_name] = {"error": str(e)}
    
    # 比较结果
    print("\n" + "=" * 60)
    print("结果比较")
    print("=" * 60)
    
    for adapter_name, data in results_comparison.items():
        if "error" in data:
            print(f"{adapter_name}: 错误 - {data['error']}")
        else:
            print(f"{adapter_name}: {data['total']} 篇论文")


def dynamic_adapter_switch():
    """动态适配器切换示例"""
    print("\n" + "=" * 60)
    print("动态适配器切换示例")
    print("=" * 60)
    
    # 创建多个服务实例
    openalex_service = LocalAcademicService(adapter_name="openalex")
    
    print("\n[场景1] 使用OpenAlex搜索基础信息")
    print("-" * 40)
    results = openalex_service.search_papers("neural networks", page_size=2)
    print(f"找到 {results.get('total', 0)} 篇论文")
    
    # 获取第一篇论文的详细信息
    if results.get("papers"):
        paper_id = results["papers"][0]["id"]
        print(f"\n获取论文详情 (ID: {paper_id})")
        paper_info = openalex_service.get_paper_info(paper_id)
        print(f"标题: {paper_info.get('title', 'N/A')[:60]}...")
        print(f"摘要: {paper_info.get('abstract', 'N/A')[:100]}...")
    
    print("\n[场景2] 切换到另一个适配器进行补充查询")
    print("-" * 40)
    print("(注: 需要配置其他API密钥才能实际运行)")
    print("示例代码:")
    print("  scopus_service = LocalAcademicService(adapter_name='scopus')")
    print("  scopus_results = scopus_service.search_papers('neural networks')")


def adapter_fallback():
    """适配器降级示例"""
    print("\n" + "=" * 60)
    print("适配器降级示例")
    print("=" * 60)
    
    # 定义适配器优先级
    adapters_priority = ["scopus", "sciencedirect", "openalex"]
    
    service = None
    active_adapter = None
    
    for adapter_name in adapters_priority:
        try:
            print(f"\n尝试初始化 {adapter_name} 适配器...")
            service = LocalAcademicService(adapter_name=adapter_name)
            active_adapter = adapter_name
            print(f"✓ {adapter_name} 适配器初始化成功")
            break
        except Exception as e:
            print(f"✗ {adapter_name} 适配器初始化失败: {e}")
            continue
    
    if service:
        print(f"\n使用 {active_adapter} 适配器执行查询")
        results = service.search_papers("deep learning", page_size=3)
        print(f"找到 {results.get('total', 0)} 篇论文")
    else:
        print("\n✗ 所有适配器都不可用")


def compare_author_data(author_name="Yann LeCun"):
    """比较不同适配器获取的作者数据"""
    print("\n" + "=" * 60)
    print(f"比较不同适配器的作者数据: {author_name}")
    print("=" * 60)
    
    adapters = ["openalex"]  # 可以添加更多适配器
    
    for adapter_name in adapters:
        print(f"\n[{adapter_name.upper()}]")
        print("-" * 40)
        
        try:
            service = LocalAcademicService(adapter_name=adapter_name)
            
            # 先搜索作者
            # 注意: 这里需要实现search_authors方法
            # results = service.search_authors(author_name)
            
            # 使用已知的作者ID示例
            author_id = "A5003442465"  # Yann LeCun in OpenAlex
            author = service.get_author_info(author_id)
            
            if author:
                print(f"姓名: {author.get('name')}")
                print(f"机构: {author.get('affiliation', 'N/A')}")
                print(f"H指数: {author.get('h_index', 'N/A')}")
                print(f"被引次数: {author.get('citations_count', 0)}")
                print(f"论文数量: {author.get('papers_count', 0)}")
            else:
                print("未找到作者信息")
                
        except Exception as e:
            print(f"错误: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("Academic Agent - 适配器切换示例")
    print("=" * 60)
    
    # 比较不同适配器
    compare_adapters(keyword="machine learning", page_size=3)
    
    # 动态切换
    dynamic_adapter_switch()
    
    # 适配器降级
    adapter_fallback()
    
    # 比较作者数据
    compare_author_data("Yann LeCun")
    
    print("\n" + "=" * 60)
    print("适配器切换示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
