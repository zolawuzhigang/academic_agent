#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复杂任务分解Agent
能够自动分解复杂问题为多个子任务，并逐一处理
"""

from academic_chat import AcademicChatAssistant
import re
from typing import List, Dict, Any


class ComplexTaskAgent:
    """复杂任务分解Agent"""
    
    def __init__(self):
        """初始化Agent"""
        self.assistant = AcademicChatAssistant()
        self.task_history = []
        
        print("🤖 复杂任务分解Agent已启动！")
        print("💡 可以处理复杂问题，自动分解为多个子任务")
        print("   - 历史问题分析")
        print("   - 多维度学术研究")
        print("   - 跨领域文献综述")
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
        
        # 检测问题特征
        features = {
            'has_multiple_entities': False,  # 多个实体
            'has_time_range': False,  # 时间范围
            'has_geographic_scope': False,  # 地理范围
            'has_causal_chain': False,  # 因果链
            'has_comparison': False,  # 对比
            'has_specific_year': False,  # 特定年份
            'requires_synthesis': False  # 需要综合
        }
        
        # 检测多个实体
        entities = re.findall(r'[\u4e00-\u9fff]{2,}|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', question)
        if len(entities) > 3:
            features['has_multiple_entities'] = True
        
        # 检测时间范围
        if re.search(r'(20世纪|上半叶|下半叶|独立|衰落|冷战|从.*到.*)', question):
            features['has_time_range'] = True
        
        # 检测地理范围
        if re.search(r'(欧洲|南亚|东亚|岛国|大陆|海峡|通道)', question):
            features['has_geographic_scope'] = True
        
        # 检测因果链
        if re.search(r'(因为|导致|由于|所以|从而|进而)', question):
            features['has_causal_chain'] = True
        
        # 检测对比
        if re.search(r'(对比|比较|区别|差异|相同)', question):
            features['has_comparison'] = True
        
        # 检测特定年份
        if re.search(r'(其中一年|同年|哪一年|哪年)', question):
            features['has_specific_year'] = True
        
        # 检测需要综合
        if re.search(r'(请问|答案是|直接回答|结论)', question):
            features['requires_synthesis'] = True
        
        # 计算复杂度
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
        
        # 分析问题特征
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
        
        # 根据问题类型生成子任务
        if analysis['features']['has_specific_year'] and analysis['features']['requires_synthesis']:
            # 需要查找特定年份的问题
            tasks.extend(self._create_year_finding_tasks(question))
        elif analysis['features']['has_multiple_entities'] and analysis['features']['has_time_range']:
            # 多实体+时间范围的问题
            tasks.extend(self._create_multi_entity_tasks(question))
        elif analysis['features']['has_comparison']:
            # 对比类问题
            tasks.extend(self._create_comparison_tasks(question))
        else:
            # 默认：分解为关键词搜索
            tasks.extend(self._create_keyword_search_tasks(question))
        
        return tasks
    
    def _create_year_finding_tasks(self, question: str) -> List[Dict[str, Any]]:
        """创建年份查找子任务"""
        tasks = []
        
        # 提取关键人物/事件
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
        
        # 提取地理实体
        geographic_entities = re.findall(r'(欧洲|南亚|东亚|岛国|大陆|海峡|通道)', question)
        for entity in geographic_entities:
            tasks.append({
                'type': 'search',
                'description': f'搜索关于{entity}的学术文献',
                'keywords': [entity],
                'priority': 'medium'
            })
        
        # 提取时间相关
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
        
        # 提取对比对象
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
        
        # 提取关键词
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
            'error': None
        }
        
        try:
            if task['type'] == 'search':
                # 执行搜索任务
                for keyword in task['keywords']:
                    search_question = f"搜索关于{keyword}的学术文献"
                    self.assistant.ask(search_question)
                    result = {
                        'keyword': keyword,
                        'found': True
                    }
                    result['status'] = 'completed'
                    return result
            
            elif task['type'] == 'llm_compare':
                # 执行LLM对比任务
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
    
    def synthesize_results(self, tasks: List[Dict[str, Any]], question: str) -> str:
        """
        综合所有子任务的结果
        
        Args:
            tasks: 子任务列表
            question: 原始问题
            
        Returns:
            综合结果
        """
        print(f"\n{'='*80}")
        print("📊 综合分析结果")
        print(f"{'='*80}\n")
        
        completed_tasks = [t for t in tasks if t['status'] == 'completed']
        failed_tasks = [t for t in tasks if t['status'] == 'failed']
        
        synthesis = f"""
## 问题分析

原始问题: {question}

## 任务执行情况

✅ 已完成任务: {len(completed_tasks)}/{len(tasks)}
❌ 失败任务: {len(failed_tasks)}/{len(tasks)}

## 综合结论

基于以上{len(completed_tasks)}个子任务的执行结果，可以得出以下结论：

"""
        
        # 根据任务类型生成综合结论
        if any('监禁' in t.get('description', '') for t in completed_tasks):
            synthesis += """
1. **关键人物识别**: 搜索结果中可能包含相关科学家/学者的信息
2. **时间线分析**: 通过文献发表时间可以推断关键年份
3. **交叉验证**: 多个来源的信息交叉验证可以提高准确性

"""
        
        if any('档案' in t.get('description', '') for t in completed_tasks):
            synthesis += """
4. **档案文献**: 相关的档案文献可能包含具体的历史记录和决定
5. **政策文献**: 法律/法规相关的文献可能包含颁布时间

"""
        
        synthesis += """
## 建议

1. 查看所有搜索结果的详细信息，特别关注年份信息
2. 使用LLM对关键文献进行深入分析
3. 交叉验证不同来源的信息
4. 如需更精确的答案，建议查阅原始档案或历史文献

"""
        
        return synthesis
    
    def process_complex_question(self, question: str):
        """
        处理复杂问题
        
        Args:
            question: 用户问题
        """
        # 记录任务
        self.task_history.append({
            'question': question,
            'timestamp': self._get_timestamp()
        })
        
        # 分解任务
        tasks = self.decompose_task(question)
        
        print(f"\n{'='*80}")
        print(f"📋 已分解为 {len(tasks)} 个子任务")
        print(f"{'='*80}\n")
        
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task['description']}")
            print(f"   优先级: {task['priority']}")
        
        # 执行任务
        results = []
        for task in tasks:
            result = self.execute_task(task)
            results.append(result)
        
        # 综合结果
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
                    print("\n👋 感谢使用复杂任务分解Agent，再见！")
                    break
                
                # 处理复杂问题
                self.process_complex_question(question)
                
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用复杂任务分解Agent，再见！")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")


def main():
    """主函数"""
    agent = ComplexTaskAgent()
    agent.run()


if __name__ == "__main__":
    main()
