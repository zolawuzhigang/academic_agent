"""
HTTP客户端示例
展示如何通过HTTP API调用 Academic Agent 服务
"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"


def print_response(response):
    """打印响应结果"""
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")


def health_check():
    """健康检查"""
    print("\n" + "=" * 60)
    print("[健康检查]")
    print("-" * 60)
    
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)


def search_papers(keyword, start_year=None, end_year=None, page_size=10):
    """搜索论文"""
    print("\n" + "=" * 60)
    print(f"[搜索论文] 关键词: {keyword}")
    print("-" * 60)
    
    payload = {
        "keyword": keyword,
        "page": 1,
        "page_size": page_size
    }
    if start_year:
        payload["start_year"] = start_year
    if end_year:
        payload["end_year"] = end_year
    
    response = requests.post(
        f"{BASE_URL}/api/papers/search",
        json=payload
    )
    
    data = response.json()
    if data.get("code") == 200:
        result = data.get("data", {})
        print(f"找到 {result.get('total', 0)} 篇论文")
        print("\n论文列表:")
        for i, paper in enumerate(result.get("papers", []), 1):
            print(f"  {i}. {paper.get('title', 'N/A')[:70]}...")
            print(f"     年份: {paper.get('publish_year')}, 被引: {paper.get('citations_count', 0)}")
    else:
        print_response(response)


def get_author_info(author_id):
    """获取作者信息"""
    print("\n" + "=" * 60)
    print(f"[获取作者信息] ID: {author_id}")
    print("-" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/author/info",
        json={"author_id": author_id}
    )
    
    data = response.json()
    if data.get("code") == 200:
        author = data.get("data", {})
        print(f"姓名: {author.get('name')}")
        print(f"机构: {author.get('affiliation', 'N/A')}")
        print(f"H指数: {author.get('h_index', 'N/A')}")
        print(f"被引次数: {author.get('citations_count', 0)}")
        print(f"论文数量: {author.get('papers_count', 0)}")
    else:
        print_response(response)


def get_author_yearly_papers(author_id, start_year, end_year):
    """获取作者年度发文统计"""
    print("\n" + "=" * 60)
    print(f"[作者年度发文统计] ID: {author_id}")
    print("-" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/analysis/author-yearly",
        json={
            "author_id": author_id,
            "start_year": start_year,
            "end_year": end_year
        }
    )
    
    data = response.json()
    if data.get("code") == 200:
        result = data.get("data", {})
        print("年度发文量:")
        for year, count in sorted(result.get("yearly_counts", {}).items()):
            bar = "█" * count
            print(f"  {year}: {bar} ({count})")
    else:
        print_response(response)


def get_author_cooperation_network(author_id, depth=1):
    """获取作者合作网络"""
    print("\n" + "=" * 60)
    print(f"[作者合作网络] ID: {author_id}")
    print("-" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/relation/author-cooperation",
        json={
            "author_id": author_id,
            "depth": depth
        }
    )
    
    data = response.json()
    if data.get("code") == 200:
        result = data.get("data", {})
        print(f"节点数: {result.get('total_nodes', 0)}")
        print(f"边数: {result.get('total_edges', 0)}")
        print(f"\n主要合作者:")
        for node in result.get("nodes", [])[:5]:
            if node.get("id") != author_id:
                print(f"  - {node.get('name')} (合作{node.get('weight', 0)}次)")
    else:
        print_response(response)


def get_research_trend(field, time_window=5):
    """获取研究趋势"""
    print("\n" + "=" * 60)
    print(f"[研究趋势分析] 领域: {field}")
    print("-" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/research/trend",
        json={
            "field": field,
            "time_window": time_window
        }
    )
    
    data = response.json()
    if data.get("code") == 200:
        result = data.get("data", {})
        print(f"年度趋势:")
        for year, year_data in sorted(result.get("yearly_trend", {}).items()):
            print(f"  {year}: {year_data.get('paper_count')} 篇论文")
        
        print(f"\n新兴主题:")
        for topic in result.get("emerging_topics", [])[:5]:
            print(f"  - {topic}")
    else:
        print_response(response)


def get_research_gaps(field, sub_field=None):
    """获取研究空白"""
    print("\n" + "=" * 60)
    print(f"[研究空白识别] 领域: {field}")
    print("-" * 60)
    
    payload = {"field": field}
    if sub_field:
        payload["sub_field"] = sub_field
    
    response = requests.post(
        f"{BASE_URL}/api/research/gap",
        json=payload
    )
    
    data = response.json()
    if data.get("code") == 200:
        result = data.get("data", {})
        print(f"潜在研究空白:")
        for gap in result.get("potential_research_gaps", [])[:5]:
            print(f"  - {gap}")
    else:
        print_response(response)


def get_top_cited_papers(keyword, start_year, end_year, top_n=5):
    """获取高被引论文"""
    print("\n" + "=" * 60)
    print(f"[高被引论文] 关键词: {keyword}")
    print("-" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/analysis/top-cited",
        json={
            "keyword": keyword,
            "start_year": start_year,
            "end_year": end_year,
            "top_n": top_n
        }
    )
    
    data = response.json()
    if data.get("code") == 200:
        result = data.get("data", {})
        print(f"Top {top_n} 高被引论文:")
        for i, paper in enumerate(result.get("papers", []), 1):
            print(f"  {i}. {paper.get('title', 'N/A')[:60]}...")
            print(f"     被引次数: {paper.get('citations_count', 0)}")
    else:
        print_response(response)


def export_data(paper_ids, format="json"):
    """导出数据"""
    print("\n" + "=" * 60)
    print(f"[数据导出] 格式: {format}")
    print("-" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/export/data",
        json={
            "paper_ids": paper_ids,
            "format": format
        }
    )
    
    data = response.json()
    if data.get("code") == 200:
        result = data.get("data", {})
        print(f"导出成功!")
        print(f"文件大小: {result.get('size', 0)} bytes")
        print(f"下载链接: {result.get('download_url', 'N/A')}")
    else:
        print_response(response)


def main():
    """主函数"""
    print("=" * 60)
    print("Academic Agent - HTTP客户端示例")
    print("=" * 60)
    print(f"API地址: {BASE_URL}")
    
    try:
        # 健康检查
        health_check()
        
        # 搜索论文
        search_papers("machine learning", start_year=2020, end_year=2024, page_size=3)
        
        # 获取作者信息
        get_author_info("A5003442465")  # Yann LeCun
        
        # 获取作者年度发文统计
        get_author_yearly_papers("A5003442465", 2018, 2023)
        
        # 获取作者合作网络
        get_author_cooperation_network("A5003442465", depth=1)
        
        # 获取研究趋势
        get_research_trend("artificial intelligence", time_window=5)
        
        # 获取研究空白
        get_research_gaps("machine learning", sub_field="federated learning")
        
        # 获取高被引论文
        get_top_cited_papers("transformer", 2017, 2024, top_n=5)
        
        # 导出数据（示例）
        # export_data(["W123456789"], format="json")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败! 请确保服务已启动:")
        print(f"   uvicorn academic_agent.services.http_service:create_app --factory")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    
    print("\n" + "=" * 60)
    print("HTTP客户端示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
