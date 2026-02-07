#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版复杂任务分解Agent
具备智能总结分析能力，使用LLM进行深度分析和推理
"""

from academic_chat import AcademicChatAssistant
from academic_agent.llm import get_llm_adapter
from academic_agent.config import load_config
import re
from typing import List, Dict, Any


class EnhancedComplexTaskAgent:
    """增强版复杂任务分解Agent，具备智能总结分析能力"""
    
    def __init__(self):
        """初始化Agent"""
        self.assistant = AcademicChatAssistant()
        self.task_history = []
        
        # 初始化LLM用于总结分析
        config = load_config()
        llm_config = config.get("llm", {}).get("zhipu", {})
        
        # 使用与 academic_chat.py 相同的方式获取LLM适配器
        self.llm_adapter = get_llm_adapter("zhipu", {
            "api_key": llm_config.get("api_key"),
            "model_name": llm_config.get("model", "qwen3-max"),
            "base_url": llm_config.get("base_url"),
            "temperature": 0.7,
            "max_tokens": 3000
        })
        
        print("🤖 增强版复杂任务分解Agent已启动！")
        print("💡 具备智能总结分析能力")
        print("   - LLM驱动的深度分析")
        print("   - 多源信息整合")
        print("   - 智能答案生成")
        print("   - 置信度评估")
        print("\n输入 'quit' 或 'exit' 退出\n")
    
    def analyze_complexity(self, question: str) -> Dict[str, Any]:
        """
        分析问题复杂度
        
        Args:
            question: 用户问题
            
        Returns:
            复杂度分析结果
        """
        question_lower = question.lower()
        
        features = {
            'has_multiple_entities': False,
            'has_time_range': False,
            'has_geographic_scope': False,
            'has_causal_chain': False,
            'has_comparison': False,
            'has_specific_year': False,
            'requires_synthesis': False
        }
        
        entities = re.findall(r'[\u4e00-\u9fff]{2,}|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', question)
        if len(entities) > 3:
            features['has_multiple_entities'] = True
        
        if re.search(r'(20世纪|上半叶|下半叶|独立|衰落|冷战|从.*到.*)', question):
            features['has_time_range'] = True
        
        if re.search(r'(欧洲|南亚|东亚|岛国|大陆|海峡|通道)', question):
            features['has_geographic_scope'] = True
        
        if re.search(r'(因为|导致|由于|所以|从而|进而)', question):
            features['has_causal_chain'] = True
        
        if re.search(r'(对比|比较|区别|差异|相同)', question):
            features['has_comparison'] = True
        
        if re.search(r'(其中一年|同年|哪一年|哪年)', question):
            features['has_specific_year'] = True
        
        if re.search(r'(请问|答案是|直接回答|结论)', question):
            features['requires_synthesis'] = True
        
        complexity_score = sum(features.values())
        
        return {
            'features': features,
            'complexity_score': complexity_score,
            'complexity_level': self._get_complexity_level(complexity_score)
        }
    
    def _get_complexity_level(self, score: int) -> str:
        """获取复杂度等级"""
        if score <= 2:
            return "简单"
        elif score <= 4:
            return "中等"
        elif score <= 6:
            return "复杂"
        else:
            return "非常复杂"
    
    def decompose_task(self, question: str) -> List[Dict[str, Any]]:
        """
        分解复杂任务为多个子任务
        
        Args:
            question: 用户问题
            
        Returns:
            子任务列表
        """
        tasks = []
        analysis = self.analyze_complexity(question)
        
        print(f"\n{'='*80}")
        print("📊 问题复杂度分析")
        print(f"{'='*80}")
        print(f"复杂度等级: {analysis['complexity_level']}")
        print(f"复杂度得分: {analysis['complexity_score']}")
        print(f"\n问题特征:")
        for feature, value in analysis['features'].items():
            if value:
                print(f"  ✓ {feature}")
        
        if analysis['features']['has_specific_year'] and analysis['features']['requires_synthesis']:
            tasks.extend(self._create_year_finding_tasks(question))
        elif analysis['features']['has_multiple_entities'] and analysis['features']['has_time_range']:
            tasks.extend(self._create_multi_entity_tasks(question))
        elif analysis['features']['has_comparison']:
            tasks.extend(self._create_comparison_tasks(question))
        else:
            tasks.extend(self._create_keyword_search_tasks(question))
        
        return tasks
    
    def _create_year_finding_tasks(self, question: str) -> List[Dict[str, Any]]:
        """创建年份查找子任务"""
        tasks = []
        
        if re.search(r'(科学家|学者|专家)', question):
            tasks.append({
                'type': 'search',
                'description': '搜索相关科学家/学者的文献',
                'keywords': ['scientist', 'scholar', 'return'],
                'priority': 'high'
            })
        
        if re.search(r'(监禁|拘留|软禁)', question):
            tasks.append({
                'type': 'search',
                'description': '搜索监禁/拘留相关的学术文献',
                'keywords': ['imprisonment', 'detention', 'house arrest'],
                'priority': 'high'
            })
        
        if re.search(r'(档案|archives|document)', question):
            tasks.append({
                'type': 'search',
                'description': '搜索档案/文献相关的学术研究',
                'keywords': ['archives', 'document', 'records'],
                'priority': 'medium'
            })
        
        if re.search(r'(颁布|决定|law|regulation)', question):
            tasks.append({
                'type': 'search',
                'description': '搜索法律/法规相关的文献',
                'keywords': ['law', 'regulation', 'policy'],
                'priority': 'medium'
            })
        
        return tasks
    
    def _create_multi_entity_tasks(self, question: str) -> List[Dict[str, Any]]:
        """创建多实体搜索子任务"""
        tasks = []
        
        geographic_entities = re.findall(r'(欧洲|南亚|东亚|岛国|大陆|海峡|通道)', question)
        for entity in geographic_entities:
            tasks.append({
                'type': 'search',
                'description': f'搜索关于{entity}的学术文献',
                'keywords': [entity],
                'priority': 'medium'
            })
        
        if re.search(r'(20世纪|上半叶|下半叶)', question):
            tasks.append({
                'type': 'search',
                'description': '搜索20世纪上半叶的历史文献',
                'keywords': ['20th century', 'early 20th century'],
                'priority': 'medium'
            })
        
        return tasks
    
    def _create_comparison_tasks(self, question: str) -> List[Dict[str, Any]]:
        """创建对比分析子任务"""
        tasks = []
        
        comparison_objects = re.findall(r'[\u4e00-\u9fff]{2,}|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', question)
        
        for obj in comparison_objects[:2]:
            tasks.append({
                'type': 'search',
                'description': f'搜索关于{obj}的学术文献',
                'keywords': [obj],
                'priority': 'high'
            })
        
        tasks.append({
            'type': 'llm_compare',
            'description': '使用LLM进行对比分析',
            'keywords': comparison_objects[:2],
            'priority': 'high'
        })
        
        return tasks
    
    def _create_keyword_search_tasks(self, question: str) -> List[Dict[str, Any]]:
        """创建关键词搜索子任务"""
        tasks = []
        
        keywords = self.assistant.extract_keywords(question)
        
        for keyword in keywords[:3]:
            tasks.append({
                'type': 'search',
                'description': f'搜索关于"{keyword}"的学术文献',
                'keywords': [keyword],
                'priority': 'medium'
            })
        
        return tasks
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个子任务
        
        Args:
            task: 子任务
            
        Returns:
            执行结果
        """
        print(f"\n{'─'*80}")
        print(f"🎯 执行任务: {task['description']}")
        print(f"   类型: {task['type']}")
        print(f"   优先级: {task['priority']}")
        print(f"{'─'*80}")
        
        result = {
            'task': task,
            'status': 'pending',
            'data': None,
            'error': None,
            'papers': []
        }
        
        try:
            if task['type'] == 'search':
                for keyword in task['keywords']:
                    search_question = f"搜索关于{keyword}的学术文献"
                    
                    papers = self._search_papers(keyword)
                    result['papers'] = papers
                    result['keyword'] = keyword
                    result['found'] = len(papers) > 0
                    result['status'] = 'completed'
                    return result
            
            elif task['type'] == 'llm_compare':
                compare_question = f"对比{task['keywords'][0]}和{task['keywords'][1]}"
                self.assistant.ask(compare_question)
                result['status'] = 'completed'
                return result
            
            else:
                result['status'] = 'skipped'
                result['error'] = f"未知任务类型: {task['type']}"
                return result
                
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            return result
    
    def _search_papers(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索论文并返回结果"""
        try:
            papers = self.assistant.service.basic_query.handle({
                "action": "search_papers",
                "keywords": keyword,
                "limit": 5
            })
            
            if papers.get("code") == 200:
                return papers.get("data", [])
            return []
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def synthesize_results(self, tasks: List[Dict[str, Any]], question: str) -> str:
        """
        使用LLM智能综合所有子任务的结果
        
        Args:
            tasks: 子任务列表
            question: 原始问题
            
        Returns:
            综合结果
        """
        print(f"\n{'='*80}")
        print("📊 智能综合分析")
        print(f"{'='*80}\n")
        
        completed_tasks = [t for t in tasks if t['status'] == 'completed']
        failed_tasks = [t for t in tasks if t['status'] == 'failed']
        
        # 收集所有搜索到的论文信息
        all_papers = []
        for task in completed_tasks:
            if 'papers' in task:
                all_papers.extend(task['papers'])
        
        # 使用LLM进行智能分析
        llm_analysis = self._llm_synthesize(question, completed_tasks, all_papers)
        
        synthesis = f"""
## 问题分析

原始问题: {question}

## 任务执行情况

✅ 已完成任务: {len(completed_tasks)}/{len(tasks)}
❌ 失败任务: {len(failed_tasks)}/{len(tasks)}
📚 搜索到论文: {len(all_papers)} 篇

## 智能综合分析

{llm_analysis}

## 搜索到的关键文献

"""
        
        # 添加前5篇论文的信息
        for i, paper in enumerate(all_papers[:5], 1):
            synthesis += f"{i}. {paper.get('title', 'N/A')}\n"
            synthesis += f"   作者: {', '.join([a.get('name', 'Unknown') if isinstance(a, dict) else str(a) for a in paper.get('authors', [])[:3]])}\n"
            synthesis += f"   年份: {paper.get('publication_year', 'N/A')}\n"
            synthesis += f"   期刊: {paper.get('venue', 'N/A')}\n\n"
        
        synthesis += """
## 建议

1. 查看所有搜索结果的详细信息，特别关注年份信息
2. 使用LLM对关键文献进行深入分析
3. 交叉验证不同来源的信息
4. 如需更精确的答案，建议查阅原始档案或历史文献

"""
        
        return synthesis
    
    def _llm_synthesize(self, question: str, tasks: List[Dict[str, Any]], papers: List[Dict[str, Any]]) -> str:
        """
        使用LLM进行智能综合分析
        
        Args:
            question: 原始问题
            tasks: 子任务列表
            papers: 搜索到的论文
            
        Returns:
            LLM分析结果
        """
        # 构建论文摘要
        papers_summary = ""
        for i, paper in enumerate(papers[:10], 1):
            authors = ', '.join([a.get('name', 'Unknown') if isinstance(a, dict) else str(a) for a in paper.get('authors', [])[:3]])
            papers_summary += f"\n论文{i}: {paper.get('title', 'N/A')}\n"
            papers_summary += f"作者: {authors}\n"
            papers_summary += f"年份: {paper.get('publication_year', 'N/A')}\n"
            papers_summary += f"摘要: {(paper.get('abstract') or 'N/A')[:200]}...\n"
        
        # 构建LLM提示词
        prompt = f"""你是一个学术研究助手，需要根据搜索到的学术文献回答用户的问题。

用户问题:
{question}

搜索到的学术文献:
{papers_summary}

请基于以上文献信息，进行以下分析:

1. **关键信息提取**: 从文献中提取与问题相关的关键信息，包括人物、事件、时间、地点等
2. **逻辑推理**: 基于提取的信息，进行逻辑推理，找出问题的答案
3. **答案生成**: 如果问题要求直接回答（如年份、数字等），请给出明确的答案
4. **置信度评估**: 评估你的答案的可信度（高/中/低），并说明理由
5. **信息缺口**: 指出搜索结果中缺失的关键信息，以及这些信息如何影响答案的准确性

请以结构化的方式输出你的分析结果。

分析结果:"""
        
        try:
            messages = [
                {"role": "system", "content": "你是一个专业的学术研究助手，擅长从学术文献中提取信息并进行逻辑推理。"},
                {"role": "user", "content": prompt}
            ]
            
            result = self.llm_adapter.chat(messages)
            return result.get("content", "LLM分析失败")
        except Exception as e:
            return f"LLM分析失败: {str(e)}"
    
    def process_complex_question(self, question: str):
        """
        处理复杂问题
        
        Args:
            question: 用户问题
        """
        self.task_history.append({
            'question': question,
            'timestamp': self._get_timestamp()
        })
        
        tasks = self.decompose_task(question)
        
        print(f"\n{'='*80}")
        print(f"📋 已分解为 {len(tasks)} 个子任务")
        print(f"{'='*80}\n")
        
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task['description']}")
            print(f"   优先级: {task['priority']}")
        
        results = []
        for task in tasks:
            result = self.execute_task(task)
            results.append(result)
        
        synthesis = self.synthesize_results(results, question)
        
        print(synthesis)
        
        return synthesis
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run(self):
        """运行交互循环"""
        while True:
            try:
                question = input("\n💬 请输入您的问题: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', '退出', 'q']:
                    print("\n👋 感谢使用增强版复杂任务分解Agent，再见！")
                    break
                
                self.process_complex_question(question)
                
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用增强版复杂任务分解Agent，再见！")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")


def main():
    """主函数"""
    agent = EnhancedComplexTaskAgent()
    agent.run()


if __name__ == "__main__":
    main()
