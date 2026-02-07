"""
LLM集成使用示例

展示如何使用LLM增强的学术分析功能
"""
from academic_agent import LocalAcademicService
from academic_agent.llm import get_llm_adapter
from academic_agent.qa import LLMEnhancedResearchModule


def main():
    """主函数"""
    print("=" * 60)
    print("Academic Agent - LLM集成使用示例")
    print("=" * 60)
    
    # 初始化学术服务
    print("\n[1] 初始化学术服务...")
    service = LocalAcademicService(adapter_name="openalex")
    print("✓ 学术服务初始化完成")
    
    # 初始化LLM（使用智谱AI作为示例）
    print("\n[2] 初始化LLM...")
    print("请确保在config.yaml中配置了LLM API Key")
    
    # 示例1：使用智谱AI
    try:
        llm_adapter = get_llm_adapter("zhipu", {
            "model_name": "glm-4",
            "api_key": "your_zhipu_api_key_here",
            "temperature": 0.7,
            "max_tokens": 2000
        })
        print(f"✓ LLM初始化完成 ({llm_adapter.provider_name})")
    except Exception as e:
        print(f"✗ LLM初始化失败: {e}")
        print("\n请先在config.yaml中配置LLM API Key")
        return
    
    # 创建LLM增强的问答模块
    llm_module = LLMEnhancedResearchModule(
        adapter=service.adapter,
        llm_adapter=llm_adapter
    )
    
    # 示例2：智能论文总结
    print("\n[3] 智能论文总结...")
    print("-" * 40)
    paper_ids = ["W2741809807", "W2914245532", "W3128426327"]
    print(f"分析论文: {len(paper_ids)} 篇")
    
    summary_result = llm_module.handle({
        "type": "smart_summary",
        "paper_ids": paper_ids
    })
    
    if summary_result.get("code") == 200:
        print("✓ 总结完成")
        print(f"\n智能总结:\n{summary_result['data']['summary']}")
    else:
        print(f"✗ 总结失败: {summary_result.get('msg')}")
    
    # 示例3：研究趋势分析
    print("\n[4] 研究趋势分析...")
    print("-" * 40)
    keyword = "transformer"
    print(f"分析关键词: {keyword}")
    
    trend_result = llm_module.handle({
        "type": "research_trend_analysis",
        "keyword": keyword,
        "start_year": 2020,
        "end_year": 2024
    })
    
    if trend_result.get("code") == 200:
        print("✓ 趋势分析完成")
        print(f"\n趋势分析:\n{trend_result['data']['trend_analysis']}")
    else:
        print(f"✗ 趋势分析失败: {trend_result.get('msg')}")
    
    # 示例4：研究空白识别
    print("\n[5] 研究空白识别...")
    print("-" * 40)
    keyword = "federated learning"
    print(f"分析领域: {keyword}")
    
    gap_result = llm_module.handle({
        "type": "research_gap_identification",
        "keyword": keyword,
        "start_year": 2020,
        "end_year": 2024
    })
    
    if gap_result.get("code") == 200:
        print("✓ 空白识别完成")
        print(f"\n研究空白:\n{gap_result['data']['research_gaps']}")
    else:
        print(f"✗ 空白识别失败: {gap_result.get('msg')}")
    
    # 示例5：论文对比分析
    print("\n[6] 论文对比分析...")
    print("-" * 40)
    paper_ids = ["W2741809807", "W2914245532"]
    print(f"对比论文: {len(paper_ids)} 篇")
    
    compare_result = llm_module.handle({
        "type": "paper_comparison",
        "paper_ids": paper_ids
    })
    
    if compare_result.get("code") == 200:
        print("✓ 对比分析完成")
        print(f"\n对比分析:\n{compare_result['data']['comparison']}")
    else:
        print(f"✗ 对比分析失败: {compare_result.get('msg')}")
    
    # 示例6：跨领域分析
    print("\n[7] 跨领域关联分析...")
    print("-" * 40)
    field1 = "computer vision"
    field2 = "natural language processing"
    print(f"分析领域: {field1} vs {field2}")
    
    cross_result = llm_module.handle({
        "type": "cross_field_analysis",
        "field1": field1,
        "field2": field2
    })
    
    if cross_result.get("code") == 200:
        print("✓ 跨领域分析完成")
        print(f"\n跨领域分析:\n{cross_result['data']['cross_field_analysis']}")
    else:
        print(f"✗ 跨领域分析失败: {cross_result.get('msg')}")
    
    # 示例7：作者研究方向演变
    print("\n[8] 作者研究方向演变分析...")
    print("-" * 40)
    author_id = "A5003442465"
    print(f"分析作者ID: {author_id}")
    
    evolution_result = llm_module.handle({
        "type": "author_research_evolution",
        "author_id": author_id
    })
    
    if evolution_result.get("code") == 200:
        print("✓ 演变分析完成")
        print(f"\n研究方向演变:\n{evolution_result['data']['research_evolution']}")
    else:
        print(f"✗ 演变分析失败: {evolution_result.get('msg')}")
    
    # 示例8：文献综述生成
    print("\n[9] 文献综述生成...")
    print("-" * 40)
    topic = "large language models"
    print(f"综述主题: {topic}")
    
    review_result = llm_module.handle({
        "type": "literature_review",
        "topic": topic,
        "start_year": 2020,
        "end_year": 2024
    })
    
    if review_result.get("code") == 200:
        print("✓ 文献综述生成完成")
        print(f"\n文献综述:\n{review_result['data']['literature_review']}")
    else:
        print(f"✗ 文献综述生成失败: {review_result.get('msg')}")
    
    print("\n" + "=" * 60)
    print("示例运行完成!")
    print("=" * 60)


def example_with_openai():
    """使用OpenAI的示例"""
    print("\n使用OpenAI GPT的示例:")
    print("-" * 40)
    
    service = LocalAcademicService(adapter_name="openalex")
    
    llm_adapter = get_llm_adapter("openai", {
        "model_name": "gpt-4",
        "api_key": "your_openai_api_key_here",
        "temperature": 0.7,
        "max_tokens": 2000
    })
    
    llm_module = LLMEnhancedResearchModule(
        adapter=service.adapter,
        llm_adapter=llm_adapter
    )
    
    result = llm_module.handle({
        "type": "smart_summary",
        "paper_ids": ["W2741809807"]
    })
    
    if result.get("code") == 200:
        print(result["data"]["summary"])


def example_with_anthropic():
    """使用Anthropic Claude的示例"""
    print("\n使用Anthropic Claude的示例:")
    print("-" * 40)
    
    service = LocalAcademicService(adapter_name="openalex")
    
    llm_adapter = get_llm_adapter("anthropic", {
        "model_name": "claude-3-sonnet-20240229",
        "api_key": "your_anthropic_api_key_here",
        "temperature": 0.7,
        "max_tokens": 2000
    })
    
    llm_module = LLMEnhancedResearchModule(
        adapter=service.adapter,
        llm_adapter=llm_adapter
    )
    
    result = llm_module.handle({
        "type": "research_trend_analysis",
        "keyword": "machine learning",
        "start_year": 2020,
        "end_year": 2024
    })
    
    if result.get("code") == 200:
        print(result["data"]["trend_analysis"])


if __name__ == "__main__":
    main()
    
    # 取消注释以使用其他LLM提供商
    # example_with_openai()
    # example_with_anthropic()
