# LLM集成使用指南

## 概述

学术Agent现已支持LLM集成，可以结合大语言模型进行智能化的学术分析。支持以下LLM提供商：

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3 Opus, Claude-3 Sonnet
- **智谱AI**: GLM-4, GLM-3-Turbo

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置LLM API Key

编辑 [config.yaml](file:///c:/Users/bigda/Desktop/Kimi_Agent_学术Agent提示词/academic_agent/config/config.yaml)，在 `llm` 部分配置您的API Key：

```yaml
llm:
  default_provider: "zhipu"
  
  # 智谱AI配置
  zhipu:
    api_key: "your_zhipu_api_key_here"
    model: "glm-4"
    temperature: 0.7
    max_tokens: 2000
```

### 3. 基础使用

```python
from academic_agent import LocalAcademicService
from academic_agent.llm import get_llm_adapter
from academic_agent.qa import LLMEnhancedResearchModule

# 初始化学术服务
service = LocalAcademicService(adapter_name="openalex")

# 初始化LLM
llm_adapter = get_llm_adapter("zhipu", {
    "model_name": "glm-4",
    "api_key": "your_api_key",
    "temperature": 0.7,
    "max_tokens": 2000
})

# 创建LLM增强模块
llm_module = LLMEnhancedResearchModule(
    adapter=service.adapter,
    llm_adapter=llm_adapter
)

# 使用LLM分析
result = llm_module.handle({
    "type": "smart_summary",
    "paper_ids": ["W2741809807", "W2914245532"]
})

print(result["data"]["summary"])
```

## 功能列表

### 1. 智能论文总结

自动对多篇论文进行智能总结，提取关键信息。

```python
result = llm_module.handle({
    "type": "smart_summary",
    "paper_ids": ["W2741809807", "W2914245532", "W3128426327"]
})
```

**返回内容**：
- 研究主题概述
- 主要研究方法
- 关键发现
- 研究趋势

### 2. 研究趋势分析

分析特定研究领域的发展趋势。

```python
result = llm_module.handle({
    "type": "research_trend_analysis",
    "keyword": "transformer",
    "start_year": 2020,
    "end_year": 2024
})
```

**返回内容**：
- 研究热点
- 技术演进方向
- 未来发展趋势

### 3. 研究空白识别

识别研究领域中的空白和机会。

```python
result = llm_module.handle({
    "type": "research_gap_identification",
    "keyword": "federated learning",
    "start_year": 2020,
    "end_year": 2024
})
```

**返回内容**：
- 当前研究的局限性
- 未解决的问题
- 潜在的研究机会

### 4. 论文对比分析

对比分析多篇论文的优缺点和方法。

```python
result = llm_module.handle({
    "type": "paper_comparison",
    "paper_ids": ["W2741809807", "W2914245532"]
})
```

**返回内容**：
- 各论文的优缺点
- 方法对比
- 适用场景分析

### 5. 跨领域关联挖掘

分析两个研究领域的交叉点。

```python
result = llm_module.handle({
    "type": "cross_field_analysis",
    "field1": "computer vision",
    "field2": "natural language processing"
})
```

**返回内容**：
- 共同研究主题
- 交叉研究的技术方法
- 跨领域应用场景
- 未来研究方向建议

### 6. 作者研究方向演变

分析作者研究方向的演变过程。

```python
result = llm_module.handle({
    "type": "author_research_evolution",
    "author_id": "A5003442465"
})
```

**返回内容**：
- 研究主题的演变过程
- 主要研究阶段和转折点
- 当前研究焦点
- 未来可能的研究方向

### 7. 文献综述生成

自动生成指定主题的文献综述。

```python
result = llm_module.handle({
    "type": "literature_review",
    "topic": "large language models",
    "start_year": 2020,
    "end_year": 2024
})
```

**返回内容**：
- 研究背景和意义
- 主要研究方法和技术
- 关键发现和进展
- 研究局限和不足
- 未来研究方向
- 主要参考文献

## 使用不同的LLM提供商

### 使用OpenAI GPT

```python
llm_adapter = get_llm_adapter("openai", {
    "model_name": "gpt-4",
    "api_key": "your_openai_api_key",
    "temperature": 0.7,
    "max_tokens": 2000
})
```

### 使用Anthropic Claude

```python
llm_adapter = get_llm_adapter("anthropic", {
    "model_name": "claude-3-sonnet-20240229",
    "api_key": "your_anthropic_api_key",
    "temperature": 0.7,
    "max_tokens": 2000
})
```

### 使用智谱AI GLM

```python
llm_adapter = get_llm_adapter("zhipu", {
    "model_name": "glm-4",
    "api_key": "your_zhipu_api_key",
    "temperature": 0.7,
    "max_tokens": 2000
})
```

## 参数说明

### LLM参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| model_name | 模型名称 | 根据提供商不同 |
| api_key | API密钥 | 必填 |
| base_url | API基础URL | 提供商默认值 |
| temperature | 温度参数（0.0-2.0） | 0.7 |
| max_tokens | 最大生成token数 | 2000 |

### Temperature参数说明

- **0.0-0.3**: 输出更确定、更保守，适合事实性回答
- **0.4-0.7**: 平衡创造性和确定性，适合大多数场景
- **0.8-2.0**: 输出更随机、更有创造性，适合头脑风暴

## 完整示例

查看 [llm_integration.py](file:///c:/Users/bigda/Desktop/Kimi_Agent_学术Agent提示词/academic_agent/examples/llm_integration.py) 获取完整的使用示例。

```bash
cd academic_agent/examples
python llm_integration.py
```

## 注意事项

1. **API Key安全**: 不要将API Key提交到版本控制系统
2. **费用控制**: LLM API调用会产生费用，请注意使用量
3. **速率限制**: 各LLM提供商都有速率限制，请合理控制请求频率
4. **缓存利用**: 学术Agent会缓存API响应，减少重复调用
5. **模型选择**: 根据任务复杂度选择合适的模型

## 故障排除

### 问题1: API Key未配置

**错误**: `ValueError: API Key未配置`

**解决**: 在config.yaml中配置对应的API Key

### 问题2: API请求失败

**错误**: `requests.exceptions.RequestException`

**解决**: 
- 检查网络连接
- 验证API Key是否正确
- 检查API额度是否充足

### 问题3: 模块导入错误

**错误**: `ModuleNotFoundError: No module named 'academic_agent.llm'`

**解决**: 确保已安装最新版本的依赖包

## 扩展开发

如需添加新的LLM提供商，请参考：

1. [base_llm.py](file:///c:/Users/bigda/Desktop/Kimi_Agent_学术Agent提示词/academic_agent/llm/base_llm.py) - LLM适配器基类
2. [openai_llm.py](file:///c:/Users/bigda/Desktop/Kimi_Agent_学术Agent提示词/academic_agent/llm/openai_llm.py) - OpenAI适配器实现示例

## 支持

如有问题，请查看：
- 项目文档: [README.md](file:///c:/Users/bigda/Desktop/Kimi_Agent_学术Agent提示词/academic_agent/README.md)
- 扩展指南: [EXTENSION_GUIDE.md](file:///c:/Users/bigda/Desktop/Kimi_Agent_学术Agent提示词/academic_agent/EXTENSION_GUIDE.md)
