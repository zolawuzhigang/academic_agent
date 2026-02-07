#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话式学术助手
"""

from academic_agent.services import LocalAcademicService
from academic_agent.llm import get_llm_adapter
from academic_agent.qa import LLMEnhancedResearchModule
from academic_agent.config import load_config
import re


class AcademicChatAssistant:
    """学术对话助手"""
    
    def __init__(self):
        """初始化助手"""
        # 加载配置
        config = load_config()
        llm_config = config.get("llm", {}).get("zhipu", {})
        
        # 初始化服务
        self.service = LocalAcademicService(adapter_name="openalex")
        
        # 初始化LLM
        self.llm_adapter = get_llm_adapter("zhipu", {
            "api_key": llm_config.get("api_key"),
            "model_name": llm_config.get("model", "qwen3-max"),
            "base_url": llm_config.get("base_url"),
            "temperature": llm_config.get("temperature", 0.7),
            "max_tokens": llm_config.get("max_tokens", 2000)
        })
        
        # 初始化LLM增强模块
        self.llm_module = LLMEnhancedResearchModule(
            adapter=self.service.adapter,
            llm_adapter=self.llm_adapter
        )
        
        print("🎓 学术助手已启动！")
        print("💡 您可以直接用中文或英文提问，例如：")
        print("   - 2024年机器学习领域有哪些重要论文？")
        print("   - 总结一下Attention Is All You Need这篇论文")
        print("   - 深度学习领域的研究趋势是什么？")
        print("   - GPT-4有哪些应用场景？")
        print("   - 搜索关于transformer的论文")
        print("   - 查询论文W2626778328的详细信息")
        print("\n输入 'quit' 或 'exit' 退出\n")
    
    def understand_question(self, question):
        """
        理解用户问题并确定操作类型
        
        Args:
            question: 用户问题
            
        Returns:
            操作类型和参数
        """
        question_lower = question.lower()
        
        # 优先检查是否包含论文ID
        if re.search(r'W\d+', question):
            # 如果包含论文ID，优先判断为详情查询
            return 'detail', question
        
        # 判断问题类型
        if re.search(r'(总结|summary|summarize)', question_lower):
            return 'summary', question
        elif re.search(r'(趋势|trend|发展|evolution)', question_lower):
            return 'trend', question
        elif re.search(r'(对比|compare|comparison)', question_lower):
            return 'compare', question
        elif re.search(r'(详情|detail|information|info)', question_lower):
            return 'detail', question
        elif re.search(r'(搜索|search|find|查找)', question_lower):
            return 'search', question
        else:
            # 默认为搜索
            return 'search', question
    
    def extract_keywords(self, question):
        """
        从问题中提取关键词
        
        Args:
            question: 用户问题
            
        Returns:
            关键词列表
        """
        # 简单的关键词提取
        keywords = []
        
        # 常见学术关键词
        academic_terms = [
            'machine learning', 'deep learning', 'neural network',
            'transformer', 'attention', 'gpt', 'bert', 'llm',
            'large language model', 'artificial intelligence', 'ai',
            'computer vision', 'nlp', 'natural language processing',
            'reinforcement learning', 'supervised learning',
            'unsupervised learning', 'clustering', 'classification'
        ]
        
        # 先查找英文术语
        for term in academic_terms:
            if term.lower() in question.lower():
                keywords.append(term)
        
        # 如果没有找到英文术语，尝试提取中文关键词
        if not keywords and re.search(r'[\u4e00-\u9fff]', question):
            # 提取中文短语
            chinese_phrases = re.findall(r'[\u4e00-\u9fff]{2,}', question)
            keywords.extend(chinese_phrases[:3])
        
        # 如果还是没有，尝试提取引号中的内容
        if not keywords:
            quoted = re.findall(r'["\']([^"\']+)["\']', question)
            keywords.extend(quoted)
        
        return keywords
    
    def handle_search(self, question):
        """处理搜索问题"""
        keywords = self.extract_keywords(question)
        
        if not keywords:
            print("❌ 无法从问题中提取关键词，请提供更具体的关键词")
            return
        
        # 使用第一个关键词搜索
        keyword = keywords[0]
        
        # 尝试提取年份
        year_match = re.search(r'(20\d{2})', question)
        start_year = int(year_match.group(1)) if year_match else None
        
        try:
            results = self.service.search_papers(
                keyword=keyword,
                start_year=start_year,
                page_size=5
            )
            
            print(f"\n🔍 搜索关键词: {keyword}")
            print(f"📊 找到 {results['total']} 篇论文\n")
            
            for i, paper in enumerate(results['papers'], 1):
                authors = [a.get('name', 'Unknown') if isinstance(a, dict) else str(a) 
                          for a in paper.get('authors', [])[:3]]
                print(f"{i}. {paper['title']}")
                print(f"   👤 作者: {', '.join(authors)}")
                print(f"   📅 年份: {paper.get('publish_year', 'N/A')}")
                print(f"   📚 期刊: {paper.get('journal', 'N/A')}")
                print(f"   🔗 被引: {paper.get('citations', 0)}")
                print()
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
    
    def handle_detail(self, question):
        """处理详情查询"""
        # 尝试提取论文ID（优先级最高）
        id_match = re.search(r'W\d+', question)
        
        if id_match:
            paper_id = id_match.group(0)
        else:
            # 尝试从问题中提取论文标题
            keywords = self.extract_keywords(question)
            if keywords:
                # 搜索论文
                results = self.service.search_papers(
                    keyword=keywords[0],
                    page_size=1
                )
                if results['papers']:
                    paper_id = results['papers'][0]['paper_id']
                else:
                    print("❌ 未找到相关论文")
                    return
            else:
                print("❌ 请提供论文ID或论文标题")
                return
        
        try:
            paper_info = self.service.get_paper_info(paper_id)
            
            if paper_info:
                print(f"\n📄 论文详情\n")
                print(f"📝 标题: {paper_info.get('title', 'N/A')}")
                print(f"📅 发表年份: {paper_info.get('publish_year', 'N/A')}")
                print(f"🔗 被引次数: {paper_info.get('citations', 0)}")
                print(f"📚 期刊: {paper_info.get('journal', 'N/A')}")
                
                authors = [a.get('name', 'N/A') if isinstance(a, dict) else str(a) 
                          for a in paper_info.get('authors', [])[:5]]
                print(f"👤 作者: {', '.join(authors)}")
                
                keywords = paper_info.get('keywords', [])
                if keywords:
                    print(f"🏷️  关键词: {', '.join(keywords[:5])}")
                
                abstract = paper_info.get('abstract', '')
                if abstract:
                    print(f"\n📖 摘要:\n{abstract[:500]}...")
            else:
                print("❌ 未找到该论文")
        except Exception as e:
            print(f"❌ 查询失败: {e}")
    
    def handle_summary(self, question):
        """处理总结问题"""
        keywords = self.extract_keywords(question)
        
        if not keywords:
            print("❌ 无法从问题中提取关键词")
            return
        
        # 搜索相关论文
        try:
            papers = self.service.search_papers(
                keyword=keywords[0],
                start_year=2023,
                page_size=3
            )
            
            if papers['papers']:
                print(f"\n🔍 找到 {len(papers['papers'])} 篇论文，正在使用LLM进行智能总结...\n")
                
                # 使用LLM进行智能总结
                result = self.llm_module.handle({
                    "type": "smart_summary",
                    "paper_ids": [p['paper_id'] for p in papers['papers']]
                })
                
                if result.get('code') == 200:
                    print(f"📊 论文数量: {result['data'].get('papers_count', 0)}")
                    print(f"🤖 分析模型: {result['data'].get('model', 'N/A')}")
                    print(f"\n📝 智能总结:\n")
                    print(result['data'].get('summary', '暂无总结'))
                else:
                    print(f"❌ LLM分析失败: {result.get('msg', '未知错误')}")
            else:
                print("❌ 未找到相关论文")
        except Exception as e:
            print(f"❌ 总结失败: {e}")
    
    def handle_trend(self, question):
        """处理趋势分析"""
        keywords = self.extract_keywords(question)
        
        if not keywords:
            print("❌ 无法从问题中提取关键词")
            return
        
        try:
            print(f"\n🔍 正在搜索 '{keywords[0]}' 相关论文并使用LLM分析趋势...\n")
            
            result = self.llm_module.handle({
                "type": "research_trend_analysis",
                "keyword": keywords[0],
                "start_year": 2022,
                "end_year": 2024
            })
            
            if result.get('code') == 200:
                print(f"📊 分析时间范围: {result['data'].get('period', 'N/A')}")
                print(f"📄 论文数量: {result['data'].get('papers_count', 0)}")
                print(f"🤖 分析模型: {result['data'].get('model', 'N/A')}")
                print(f"\n📈 趋势分析:\n")
                print(result['data'].get('trend_analysis', '暂无分析'))
            else:
                print(f"❌ LLM分析失败: {result.get('msg', '未知错误')}")
        except Exception as e:
            print(f"❌ 趋势分析失败: {e}")
    
    def handle_compare(self, question):
        """处理对比分析"""
        keywords = self.extract_keywords(question)
        
        if len(keywords) < 2:
            print("❌ 对比分析需要至少两个关键词")
            return
        
        try:
            # 搜索第一个关键词的论文
            papers1 = self.service.search_papers(
                keyword=keywords[0],
                start_year=2023,
                page_size=2
            )
            
            # 搜索第二个关键词的论文
            papers2 = self.service.search_papers(
                keyword=keywords[1],
                start_year=2023,
                page_size=2
            )
            
            all_papers = papers1['papers'] + papers2['papers']
            
            if all_papers:
                print(f"\n🔍 找到 {len(all_papers)} 篇论文，正在使用LLM进行对比分析...\n")
                
                # 使用LLM进行对比分析
                result = self.llm_module.handle({
                    "type": "paper_comparison",
                    "paper_ids": [p['paper_id'] for p in all_papers]
                })
                
                if result.get('code') == 200:
                    print(f"📊 论文数量: {result['data'].get('papers_count', 0)}")
                    print(f"🤖 分析模型: {result['data'].get('model', 'N/A')}")
                    print(f"\n📝 对比分析:\n")
                    print(result['data'].get('comparison', '暂无分析'))
                else:
                    print(f"❌ LLM分析失败: {result.get('msg', '未知错误')}")
            else:
                print("❌ 未找到相关论文")
        except Exception as e:
            print(f"❌ 对比分析失败: {e}")
    
    def ask(self, question):
        """
        处理用户问题
        
        Args:
            question: 用户问题
        """
        question_type, _ = self.understand_question(question)
        
        print(f"\n{'='*80}")
        print(f"❓ 您的问题: {question}")
        print(f"{'='*80}\n")
        
        # 根据问题类型调用相应的处理函数
        handlers = {
            'search': self.handle_search,
            'detail': self.handle_detail,
            'summary': self.handle_summary,
            'trend': self.handle_trend,
            'compare': self.handle_compare
        }
        
        handler = handlers.get(question_type, self.handle_search)
        handler(question)
    
    def run(self):
        """运行对话循环"""
        while True:
            try:
                question = input("\n💬 请输入您的问题: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', '退出', 'q']:
                    print("\n👋 感谢使用学术助手，再见！")
                    break
                
                self.ask(question)
                
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用学术助手，再见！")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")


def main():
    """主函数"""
    assistant = AcademicChatAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
