# Academic Agent - 学术研究智能助手

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 低耦合、可插拔的学术研究Agent，支持对接Scopus、ScienceDirect、OpenAlex等学术API，提供从基础查询到深度分析的全场景学术研究问答能力。

## 核心特性

- **多API支持**: 对接OpenAlex（开放）、Scopus、ScienceDirect等主流学术数据库
- **低耦合架构**: 模块化设计，各层独立，通过标准化接口交互
- **可插拔设计**: 支持动态添加/移除API适配器和问答场景模块
- **全场景覆盖**: 基础查询 → 统计分析 → 关联分析 → 深度研究 → 定制化输出
- **多部署形态**: 支持本地模块调用、HTTP服务、第三方集成

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/academic-agent.git
cd academic-agent

# 安装依赖
pip install -r requirements.txt
```

### 配置

编辑 `config/config.yaml` 配置文件：

```yaml
apis:
  openalex:
    base_url: "https://api.openalex.org"
    rate_limit: 10
  
  scopus:
    api_key: "YOUR_SCOPUS_API_KEY"  # 需要申请
    rate_limit: 0.8
  
  sciencedirect:
    api_key: "YOUR_SCIENCEDIRECT_API_KEY"  # 需要申请
    rate_limit: 0.5
```

### 使用示例

#### 方式1: 本地模块调用

```python
from academic_agent import LocalAcademicService

# 初始化服务（使用OpenAlex适配器）
service = LocalAcademicService(adapter_name="openalex")

# 搜索论文
results = service.search_papers("machine learning", start_year=2020, end_year=2024)
print(f"找到 {results['total']} 篇论文")

# 获取作者信息
author = service.get_author_info("A123456789")
print(f"作者: {author['name']}, H指数: {author['h_index']}")

# 获取作者年度发文统计
stats = service.get_author_yearly_papers("A123456789", 2018, 2023)
print(stats['yearly_counts'])

# 获取作者合作网络
network = service.get_author_cooperation_network("A123456789", depth=1)
print(f"合作者数量: {network['total_nodes'] - 1}")
```

#### 方式2: HTTP服务

```bash
# 启动服务
python -m academic_agent.services.http_service

# 或使用uvicorn
uvicorn academic_agent.services.http_service:create_app --factory --host 0.0.0.0 --port 8000
```

访问 API 文档: http://localhost:8000/docs

```python
import requests

# 搜索论文
response = requests.post("http://localhost:8000/api/papers/search", json={
    "keyword": "deep learning",
    "start_year": 2020,
    "end_year": 2024,
    "page": 1,
    "page_size": 20
})
data = response.json()
print(data['data']['papers'])

# 获取研究趋势
response = requests.post("http://localhost:8000/api/research/trend", json={
    "field": "artificial intelligence",
    "time_window": 5
})
trend = response.json()
print(trend['data']['emerging_topics'])
```

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                        服务层 (Service)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Local Module │  │ HTTP Service │  │   SDK Call   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        问答层 (QA)                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Basic   │ │  Stats   │ │ Relation │ │  Deep    │       │
│  │  Query   │ │ Analysis │ │ Analysis │ │ Research │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      处理层 (Processor)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │  Clean   │  │  Cache   │  │ Convert  │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      适配层 (Adapter)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ OpenAlex │  │  Scopus  │  │  SciDir  │  + 更多...        │
│  └──────────┘  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### 模块职责

| 层级 | 模块 | 职责 |
|------|------|------|
| 服务层 | `local_service.py` | 提供本地Python API调用 |
| 服务层 | `http_service.py` | 提供HTTP RESTful API |
| 问答层 | `basic_query.py` | 基础查询（论文、作者信息） |
| 问答层 | `statistical_analysis.py` | 统计分析（发文量、被引量） |
| 问答层 | `relation_analysis.py` | 关联分析（合作网络、共现） |
| 问答层 | `deep_research.py` | 深度研究（趋势、空白） |
| 问答层 | `custom_output.py` | 定制化输出（导出、批量） |
| 处理层 | `data_cleaner.py` | 数据清洗、去重 |
| 处理层 | `data_cache.py` | 缓存管理 |
| 处理层 | `data_converter.py` | 数据格式转换 |
| 适配层 | `*_adapter.py` | 对接各学术API |

## API接口列表

### 基础查询接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/paper/info` | POST | 获取论文详细信息 |
| `/api/author/info` | POST | 获取作者详细信息 |
| `/api/author/papers` | POST | 获取作者论文列表 |
| `/api/papers/search` | POST | 搜索论文 |

### 统计分析接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/analysis/author-yearly` | POST | 作者年度发文量统计 |
| `/api/analysis/keyword-yearly` | POST | 关键词年度发表量统计 |
| `/api/analysis/top-cited` | POST | 高被引论文TopN |

### 关联分析接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/relation/author-cooperation` | POST | 作者合作网络分析 |
| `/api/relation/keyword-cooccurrence` | POST | 关键词共现分析 |
| `/api/relation/citation` | POST | 论文引证关系分析 |
| `/api/relation/institution-cooperation` | POST | 机构合作分析 |

### 深度研究接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/research/trend` | POST | 研究方向前沿趋势分析 |
| `/api/research/gap` | POST | 研究空白识别 |
| `/api/research/cross-field` | POST | 跨领域研究关联挖掘 |
| `/api/research/author-evolution` | POST | 作者研究方向演变分析 |

### 定制化输出接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/export/data` | POST | 数据导出 |
| `/api/export/batch` | POST | 批量数据导出 |

## 项目结构

```
academic_agent/
├── adapters/          # API适配器层
│   ├── base_adapter.py
│   ├── openalex_adapter.py
│   ├── scopus_adapter.py
│   ├── sciencedirect_adapter.py
│   └── __init__.py
├── models/            # 数据模型层
│   ├── paper.py
│   ├── author.py
│   ├── journal.py
│   └── __init__.py
├── processors/        # 数据处理层
│   ├── data_cleaner.py
│   ├── data_cache.py
│   ├── data_converter.py
│   └── __init__.py
├── qa/                # 问答层
│   ├── base_qa.py
│   ├── basic_query.py
│   ├── statistical_analysis.py
│   ├── relation_analysis.py
│   ├── deep_research.py
│   ├── custom_output.py
│   └── __init__.py
├── services/          # 服务层
│   ├── local_service.py
│   ├── http_service.py
│   └── __init__.py
├── config/            # 配置层
│   ├── config.yaml
│   └── __init__.py
├── exceptions/        # 异常定义层
│   ├── base_error.py
│   ├── api_error.py
│   ├── data_error.py
│   └── __init__.py
├── utils/             # 工具层
│   ├── request_utils.py
│   ├── format_utils.py
│   └── __init__.py
├── tests/             # 测试目录
├── examples/          # 示例代码
├── requirements.txt
└── __init__.py
```

## 扩展开发

### 添加新的API适配器

```python
from academic_agent.adapters import BaseAcademicAdapter
from academic_agent.models import Paper, Author

class MyAdapter(BaseAcademicAdapter):
    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        # 实现获取论文逻辑
        pass
    
    def search_papers(self, keyword: str, ...) -> List[Paper]:
        # 实现搜索逻辑
        pass
    
    # ... 实现其他抽象方法

# 注册适配器
# 在 adapters/__init__.py 中添加
adapter_map["myadapter"] = "academic_agent.adapters.my_adapter.MyAdapter"
```

### 添加新的问答模块

```python
from academic_agent.qa import BaseQAModule

class MyQAModule(BaseQAModule):
    def handle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query_type = params.get("type")
        
        if query_type == "my_query":
            return self._my_query(params)
        
        return {"code": 400, "msg": "不支持的查询类型"}
    
    def _my_query(self, params):
        # 实现查询逻辑
        return {"code": 200, "data": result, "msg": "success"}
```

更多扩展开发详情，请参考 [EXTENSION_GUIDE.md](./EXTENSION_GUIDE.md)。

## 部署指南

详细部署说明请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)。

快速部署：

```bash
# 本地部署
pip install -r requirements.txt
uvicorn academic_agent.services.http_service:create_app --factory

# Docker部署
docker build -t academic-agent:latest .
docker run -p 8000:8000 academic-agent:latest
```

## 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定模块测试
pytest tests/test_adapters/

# 生成测试报告
pytest tests/ --html=report.html
```

测试报告请参考 [TEST_REPORT.md](./TEST_REPORT.md)。

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT License

## 致谢

- [OpenAlex](https://openalex.org/) - 开放学术数据平台
- [Scopus](https://www.scopus.com/) - Elsevier学术数据库
- [ScienceDirect](https://www.sciencedirect.com/) - Elsevier全文数据库
