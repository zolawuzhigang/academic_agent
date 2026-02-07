# 学术对话助手使用说明

## 🎓 功能介绍

学术对话助手是一个基于自然语言的学术研究工具，您可以直接用中文或英文提问，助手会自动：

1. 🔍 搜索相关论文
2. 📊 查询论文详情
3. 🤖 使用LLM进行智能分析和总结
4. 📈 分析研究趋势
5. 📝 生成文献综述

## 🚀 快速开始

### 启动助手

在终端中运行：

```bash
python academic_chat.py
```

### 退出助手

输入以下任意命令退出：
- `quit`
- `exit`
- `退出`
- `q`

## 💬 提问示例

### 1. 搜索论文

**中文：**
```
2024年机器学习领域有哪些重要论文？
搜索关于transformer的论文
查找深度学习相关的研究
```

**英文：**
```
Search papers about machine learning
Find papers on deep learning
```

### 2. 查询论文详情

**中文：**
```
查询论文W2626778328的详细信息
Attention Is All You Need这篇论文的详情
```

**英文：**
```
Get details of paper W2626778328
Information about Attention Is All You Need
```

### 3. 智能总结（使用LLM）

**中文：**
```
总结一下GPT-4相关的研究
请总结transformer领域的进展
```

**英文：**
```
Summarize research on GPT-4
Summarize transformer research
```

### 4. 趋势分析（使用LLM）

**中文：**
```
深度学习领域的研究趋势是什么？
大语言模型的发展方向
```

**英文：**
```
What are the research trends in deep learning?
Trends in large language models
```

### 5. 对比分析（使用LLM）

**中文：**
```
对比GPT-4和BERT的研究
比较transformer和CNN
```

**英文：**
```
Compare GPT-4 and BERT
Compare transformer and CNN
```

## 🎯 支持的关键词

助手可以识别以下学术关键词：

- **机器学习**：machine learning, deep learning, neural network
- **AI模型**：transformer, attention, GPT, BERT, LLM
- **AI领域**：artificial intelligence, AI, computer vision, NLP
- **学习类型**：reinforcement learning, supervised learning, unsupervised learning
- **任务类型**：clustering, classification

## 📋 使用技巧

1. **使用具体的关键词**：助手会从您的问题中提取关键词进行搜索
2. **指定年份**：可以在问题中包含年份，如"2024年的论文"
3. **使用论文ID**：查询详情时，直接使用论文ID（如W2626778328）会更准确
4. **中英文皆可**：助手支持中文和英文提问

## 🔧 配置说明

助手使用 `config.yaml` 中的配置：

- **学术数据源**：OpenAlex（免费，无需API Key）
- **LLM服务**：千问AI（需要配置API Key）

配置文件位置：`academic_agent/config/config.yaml`

## ⚠️ 注意事项

1. **LLM功能需要时间**：使用LLM进行智能分析时，可能需要几秒到几十秒
2. **网络连接**：需要稳定的网络连接访问OpenAlex和千问API
3. **API限制**：OpenAlex有频率限制（10次/秒），千问API可能有调用限制

## 📚 示例对话

```
🎓 学术助手已启动！
💡 您可以直接用中文或英文提问，例如：
   - 2024年机器学习领域有哪些重要论文？
   - 总结一下Attention Is All You Need这篇论文
   - 深度学习领域的研究趋势是什么？
   - GPT-4有哪些应用场景？
   - 搜索关于transformer的论文
   - 查询论文W2626778328的详细信息

输入 'quit' 或 'exit' 退出

💬 请输入您的问题: 2024年机器学习领域有哪些重要论文？

================================================================================
❓ 您的问题: 2024年机器学习领域有哪些重要论文？
================================================================================

🔍 搜索关键词: machine learning
📊 找到 5 篇论文

1. Evaluation metrics and statistical tests for machine learning
   👤 作者: Oona Rainio, Jarmo Teuho, Riku Klén
   📅 年份: 2024
   📚 期刊: Scientific Reports
   🔗 被引: 764

2. TRIPOD+AI statement: updated guidance for reporting clinical prediction models
   👤 作者: Gary S. Collins, Karel G.M. Moons, Paula Dhiman
   📅 年份: 2024
   📚 期刊: BMJ
   🔗 被引: 1242

...

💬 请输入您的问题: 总结一下GPT-4相关的研究

================================================================================
❓ 您的问题: 总结一下GPT-4相关的研究
================================================================================

🔍 找到 2 篇论文，正在使用LLM进行智能总结...

📊 论文数量: 2
🤖 分析模型: qwen3-max

📝 智能总结:

**研究主题概述**
两篇论文均聚焦于大语言模型（LLM）的前沿探索...
...

💬 请输入您的问题: quit

👋 感谢使用学术助手，再见！
```

## 🎉 开始使用

现在就运行以下命令开始使用：

```bash
python academic_chat.py
```

享受您的学术研究之旅！🚀
