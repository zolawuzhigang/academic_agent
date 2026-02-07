"""
学术Agent SDK调用示例

本示例展示如何使用学术Agent的本地服务和HTTP服务
"""

# ==================== 本地服务使用示例 ====================

def local_service_example():
    """本地服务SDK调用示例"""
    from academic_agent.services import LocalAcademicService
    
    # 初始化服务（使用OpenAlex适配器）
    service = LocalAcademicService(adapter_name="openalex")
    
    # 基础查询示例
    print("=== 基础查询 ===")
    
    # 搜索论文
    papers = service.search_papers(
        keyword="machine learning",
        start_year=2020,
        end_year=2024,
        page=1,
        page_size=10
    )
    print(f"搜索到 {len(papers.get('results', []))} 篇论文")
    
    # 获取论文详情
    paper_info = service.get_paper_info("W123456789")
    if paper_info:
        print(f"论文标题: {paper_info.get('title')}")
    
    # 获取作者信息
    author_info = service.get_author_info("A123456789")
    if author_info:
        print(f"作者姓名: {author_info.get('name')}")
    
    # 获取作者论文列表
    author_papers = service.get_author_papers(
        author_id="A123456789",
        start_year=2020,
        end_year=2024,
        limit=50
    )
    print(f"作者论文数量: {len(author_papers)}")
    
    # 统计分析示例
    print("\n=== 统计分析 ===")
    
    # 作者年度发文量统计
    yearly_stats = service.get_author_yearly_papers(
        author_id="A123456789",
        start_year=2019,
        end_year=2024
    )
    print(f"年度发文统计: {yearly_stats}")
    
    # 关键词年度发表量统计
    keyword_stats = service.get_keyword_yearly_stats(
        keyword="deep learning",
        start_year=2019,
        end_year=2024
    )
    print(f"关键词年度统计: {keyword_stats}")
    
    # 高被引论文TopN
    top_cited = service.get_top_cited_papers(
        field="artificial intelligence",
        top_n=10,
        start_year=2020,
        end_year=2024
    )
    print(f"高被引论文数量: {len(top_cited.get('papers', []))}")
    
    # 关联分析示例
    print("\n=== 关联分析 ===")
    
    # 作者合作网络
    cooperation_network = service.get_author_cooperation_network(
        author_id="A123456789",
        depth=1,
        min_cooperations=2
    )
    print(f"合作网络节点数: {len(cooperation_network.get('nodes', []))}")
    
    # 关键词共现分析
    cooccurrence = service.get_keyword_cooccurrence(
        keyword="neural network",
        top_n=20,
        start_year=2020,
        end_year=2024
    )
    print(f"共现关键词数量: {len(cooccurrence.get('cooccurrences', []))}")
    
    # 论文引证关系
    citation_relations = service.get_citation_relations(
        paper_id="W123456789",
        depth=1
    )
    print(f"引用数量: {len(citation_relations.get('citations', []))}")
    
    # 机构合作分析
    institution_coop = service.get_institution_cooperation(
        institution="MIT",
        field="computer science",
        top_n=10
    )
    print(f"合作机构数量: {len(institution_coop.get('partners', []))}")
    
    # 深度研究示例
    print("\n=== 深度研究 ===")
    
    # 研究方向前沿趋势
    research_trend = service.get_research_trend(
        field="natural language processing",
        time_window=5
    )
    print(f"热门研究方向: {research_trend.get('trends', [])}")
    
    # 研究空白识别
    research_gaps = service.get_research_gaps(
        field="computer vision",
        sub_field="medical imaging"
    )
    print(f"研究空白: {research_gaps.get('gaps', [])}")
    
    # 跨领域研究关联
    cross_field = service.get_cross_field_analysis(
        field1="machine learning",
        field2="biology"
    )
    print(f"跨领域关联: {cross_field.get('connections', [])}")
    
    # 作者研究方向演变
    author_evolution = service.get_author_evolution(
        author_id="A123456789",
        time_window=10
    )
    print(f"研究方向演变: {author_evolution.get('evolution', [])}")
    
    # 定制化输出示例
    print("\n=== 定制化输出 ===")
    
    # 导出数据
    export_result = service.export_data(
        data_type="papers",
        params={"keyword": "AI", "year": 2023},
        format="json"
    )
    print(f"导出结果: {export_result}")
    
    # 生成图表数据
    chart_data = service.generate_chart_data(
        analysis_type="yearly_trend",
        keyword="blockchain",
        start_year=2019,
        end_year=2024
    )
    print(f"图表数据点数: {len(chart_data.get('data', []))}")
    
    # 批量导出
    batch_result = service.batch_export(
        keyword_list=["AI", "ML", "DL"],
        start_year=2020,
        end_year=2024,
        format="jsonl"
    )
    print(f"批量导出结果: {batch_result}")
    
    # 工具方法示例
    print("\n=== 工具方法 ===")
    
    # 获取缓存统计
    cache_stats = service.get_cache_stats()
    print(f"缓存统计: {cache_stats}")
    
    # 切换适配器
    service.switch_adapter("scopus")
    print(f"当前适配器: {service.adapter_name}")
    
    # 清空缓存
    cleared = service.clear_cache()
    print(f"缓存已清空: {cleared}")


# ==================== HTTP服务使用示例 ====================

def http_service_example():
    """HTTP服务启动和使用示例"""
    from academic_agent.services import start_server, create_app
    
    # 方式1: 直接启动服务器
    # start_server(adapter_name="openalex", host="0.0.0.0", port=8000)
    
    # 方式2: 创建FastAPI应用（用于集成到其他服务）
    app = create_app(adapter_name="openalex")
    
    # 可以使用uvicorn运行
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    
    print("HTTP服务已创建，API文档地址: http://localhost:8000/docs")
    print("\n可用API端点:")
    print("  POST /api/paper/info - 获取论文详情")
    print("  POST /api/author/info - 获取作者详情")
    print("  POST /api/author/papers - 获取作者论文列表")
    print("  POST /api/papers/search - 搜索论文")
    print("  POST /api/analysis/author-yearly - 作者年度发文统计")
    print("  POST /api/analysis/keyword-yearly - 关键词年度统计")
    print("  POST /api/analysis/top-cited - 高被引论文TopN")
    print("  POST /api/relation/author-cooperation - 作者合作网络")
    print("  POST /api/relation/keyword-cooccurrence - 关键词共现分析")
    print("  POST /api/relation/citation - 论文引证关系")
    print("  POST /api/relation/institution-cooperation - 机构合作分析")
    print("  POST /api/research/trend - 研究方向趋势")
    print("  POST /api/research/gap - 研究空白识别")
    print("  POST /api/research/cross-field - 跨领域分析")
    print("  POST /api/research/author-evolution - 作者研究方向演变")
    print("  POST /api/export/data - 数据导出")
    print("  POST /api/export/batch - 批量导出")
    print("  GET  /health - 健康检查")
    print("  GET  /api/system/cache-stats - 缓存统计")
    print("  POST /api/system/clear-cache - 清空缓存")


# ==================== HTTP客户端调用示例 ====================

def http_client_example():
    """HTTP客户端调用示例"""
    import requests
    
    BASE_URL = "http://localhost:8000"
    
    # 健康检查
    response = requests.get(f"{BASE_URL}/health")
    print(f"健康检查: {response.json()}")
    
    # 搜索论文
    response = requests.post(
        f"{BASE_URL}/api/papers/search",
        json={
            "keyword": "machine learning",
            "start_year": 2020,
            "end_year": 2024,
            "page": 1,
            "page_size": 10
        }
    )
    result = response.json()
    print(f"搜索结果: {result}")
    
    # 获取作者年度发文统计
    response = requests.post(
        f"{BASE_URL}/api/analysis/author-yearly",
        json={
            "author_id": "A123456789",
            "start_year": 2019,
            "end_year": 2024
        }
    )
    result = response.json()
    print(f"年度统计: {result}")
    
    # 获取合作网络
    response = requests.post(
        f"{BASE_URL}/api/relation/author-cooperation",
        json={
            "author_id": "A123456789",
            "depth": 1,
            "min_cooperations": 2
        }
    )
    result = response.json()
    print(f"合作网络: {result}")


if __name__ == "__main__":
    print("=" * 60)
    print("学术Agent SDK调用示例")
    print("=" * 60)
    
    # 本地服务示例
    print("\n" + "=" * 60)
    print("本地服务示例")
    print("=" * 60)
    # local_service_example()  # 取消注释以运行
    
    # HTTP服务示例
    print("\n" + "=" * 60)
    print("HTTP服务示例")
    print("=" * 60)
    http_service_example()
    
    # HTTP客户端示例
    print("\n" + "=" * 60)
    print("HTTP客户端示例")
    print("=" * 60)
    # http_client_example()  # 取消注释以运行（需要先启动HTTP服务）
