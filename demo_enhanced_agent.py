#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示增强版复杂任务Agent的功能
"""

from enhanced_complex_agent import EnhancedComplexTaskAgent


def demo_enhanced_agent():
    """演示增强版复杂任务Agent"""
    
    print("=" * 80)
    print("🧪 增强版复杂任务Agent演示")
    print("=" * 80)
    print()
    
    # 创建增强版复杂任务Agent
    agent = EnhancedComplexTaskAgent()
    
    # 演示问题
    question = "2024年机器学习领域有哪些重要论文？"
    
    print(f"\n💬 演示问题: {question}")
    print("=" * 80)
    print()
    
    # 处理问题
    result = agent.process_complex_question(question)
    
    print("\n" + "=" * 80)
    print("🎉 演示完成！")
    print("=" * 80)
    
    return result


if __name__ == "__main__":
    demo_enhanced_agent()
