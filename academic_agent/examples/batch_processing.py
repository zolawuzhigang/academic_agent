"""
批量处理示例
展示如何批量处理大量学术数据
"""
from academic_agent import LocalAcademicService
from academic_agent.processors import DataCache
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json


def batch_search_papers(service, keywords, start_year=2020, end_year=2024):
    """批量搜索多个关键词的论文"""
    print("\n[批量搜索论文]")
    print("-" * 40)
    
    results = {}
    total_papers = 0
    
    for keyword in keywords:
        print(f"搜索: {keyword}...", end=" ")
        start_time = time.time()
        
        result = service.search_papers(
            keyword=keyword,
            start_year=start_year,
            end_year=end_year,
            page_size=20
        )
        
        elapsed = time.time() - start_time
        count = len(result.get("papers", []))
        total_papers += count
        results[keyword] = result
        
        print(f"✓ 找到 {count} 篇 ({elapsed:.2f}s)")
    
    print(f"\n总计: {len(keywords)} 个关键词, {total_papers} 篇论文")
    return results


def parallel_batch_search(service, keywords, max_workers=3):
    """并行批量搜索"""
    print("\n[并行批量搜索]")
    print("-" * 40)
    
    results = {}
    
    def search_single(keyword):
        return keyword, service.search_papers(keyword, page_size=10)
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(search_single, kw): kw for kw in keywords}
        
        for future in as_completed(futures):
            keyword, result = future.result()
            count = len(result.get("papers", []))
            results[keyword] = result
            print(f"✓ {keyword}: {count} 篇")
    
    elapsed = time.time() - start_time
    print(f"\n并行处理完成: {elapsed:.2f}s")
    
    return results


def batch_get_author_info(service, author_ids):
    """批量获取作者信息"""
    print("\n[批量获取作者信息]")
    print("-" * 40)
    
    authors = {}
    
    for author_id in author_ids:
        print(f"获取: {author_id}...", end=" ")
        
        author = service.get_author_info(author_id)
        if author:
            authors[author_id] = author
            print(f"✓ {author.get('name', 'N/A')}")
        else:
            print(f"✗ 未找到")
    
    print(f"\n总计: {len(author_ids)} 个作者, {len(authors)} 个成功")
    return authors


def batch_analyze_trends(service, fields, time_window=5):
    """批量分析多个领域的研究趋势"""
    print("\n[批量趋势分析]")
    print("-" * 40)
    
    trends = {}
    
    for field in fields:
        print(f"分析: {field}...", end=" ")
        start_time = time.time()
        
        trend = service.get_research_trend(field, time_window=time_window)
        trends[field] = trend
        
        elapsed = time.time() - start_time
        print(f"✓ ({elapsed:.2f}s)")
    
    # 汇总结果
    print("\n趋势汇总:")
    for field, trend in trends.items():
        total_papers = sum(
            data.get('paper_count', 0) 
            for data in trend.get('yearly_trend', {}).values()
        )
        print(f"  {field}: {total_papers} 篇论文")
    
    return trends


def cached_batch_processing(service, keywords, cache_ttl=3600):
    """带缓存的批量处理"""
    print("\n[带缓存的批量处理]")
    print("-" * 40)
    
    cache = DataCache({"ttl": cache_ttl})
    results = {}
    
    for keyword in keywords:
        cache_key = f"search:{keyword}"
        
        # 尝试从缓存获取
        cached = cache.get(cache_key)
        if cached:
            print(f"{keyword}: ✓ 缓存命中")
            results[keyword] = cached
            continue
        
        # 从API获取
        print(f"{keyword}: 从API获取...", end=" ")
        result = service.search_papers(keyword, page_size=10)
        
        # 存入缓存
        cache.set(cache_key, result)
        print(f"✓ 已缓存")
        
        results[keyword] = result
    
    return results


def batch_export_with_progress(service, keywords, output_dir):
    """批量导出带进度显示"""
    print("\n[批量导出]")
    print("-" * 40)
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    total = len(keywords)
    for i, keyword in enumerate(keywords, 1):
        progress = (i / total) * 100
        print(f"[{i}/{total}] {progress:.0f}% - 导出: {keyword}")
        
        # 搜索论文
        results = service.search_papers(keyword, page_size=20)
        papers = results.get("papers", [])
        
        # 保存为JSON
        filename = keyword.replace(' ', '_') + '.json'
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ {len(papers)} 篇论文 -> {filepath}")
    
    print(f"\n导出完成: {total} 个文件")


def incremental_processing(service, keyword, batch_size=100):
    """增量处理大量数据"""
    print(f"\n[增量处理] 关键词: {keyword}")
    print("-" * 40)
    
    all_papers = []
    page = 1
    max_pages = 5  # 限制最大页数
    
    while page <= max_pages:
        print(f"获取第 {page} 页...", end=" ")
        
        results = service.search_papers(
            keyword=keyword,
            page=page,
            page_size=batch_size
        )
        
        papers = results.get("papers", [])
        if not papers:
            print("✗ 无更多数据")
            break
        
        all_papers.extend(papers)
        print(f"✓ {len(papers)} 篇")
        
        # 检查是否还有更多数据
        if len(papers) < batch_size:
            break
        
        page += 1
        
        # 添加延迟避免触发频率限制
        time.sleep(1)
    
    print(f"\n总计: {len(all_papers)} 篇论文")
    return all_papers


def compare_processing_modes(service, keywords):
    """比较串行和并行处理模式"""
    print("\n[处理模式比较]")
    print("-" * 40)
    
    # 串行处理
    print("\n1. 串行处理")
    start = time.time()
    serial_results = batch_search_papers(service, keywords)
    serial_time = time.time() - start
    print(f"串行耗时: {serial_time:.2f}s")
    
    # 并行处理
    print("\n2. 并行处理")
    start = time.time()
    parallel_results = parallel_batch_search(service, keywords, max_workers=3)
    parallel_time = time.time() - start
    print(f"并行耗时: {parallel_time:.2f}s")
    
    # 比较结果
    print("\n比较结果:")
    print(f"  串行: {serial_time:.2f}s")
    print(f"  并行: {parallel_time:.2f}s")
    if parallel_time < serial_time:
        speedup = serial_time / parallel_time
        print(f"  加速比: {speedup:.2f}x")
    else:
        print(f"  并行未带来性能提升")


def main():
    """主函数"""
    print("=" * 60)
    print("Academic Agent - 批量处理示例")
    print("=" * 60)
    
    # 初始化服务
    print("\n[初始化服务]")
    service = LocalAcademicService(adapter_name="openalex")
    print("✓ 服务初始化完成")
    
    # 定义关键词列表
    keywords = [
        "machine learning",
        "deep learning",
        "neural networks",
        "computer vision",
        "natural language processing"
    ]
    
    # 批量搜索
    batch_search_papers(service, keywords[:3])
    
    # 并行批量搜索
    parallel_batch_search(service, keywords[:3], max_workers=3)
    
    # 批量获取作者信息
    author_ids = [
        "A5003442465",  # Yann LeCun
        "A2203914028",  # Geoffrey Hinton
        # 添加更多作者ID
    ]
    batch_get_author_info(service, author_ids)
    
    # 批量趋势分析
    fields = [
        "artificial intelligence",
        "machine learning",
        "data science"
    ]
    batch_analyze_trends(service, fields, time_window=3)
    
    # 带缓存的批量处理
    cached_batch_processing(service, keywords[:3])
    
    # 增量处理
    incremental_processing(service, "machine learning", batch_size=20)
    
    # 处理模式比较
    compare_processing_modes(service, keywords[:3])
    
    # 批量导出
    import os
    batch_export_with_progress(service, keywords[:3], "./batch_export")
    
    print("\n" + "=" * 60)
    print("批量处理示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
