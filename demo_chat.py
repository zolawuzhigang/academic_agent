#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术助手功能演示
"""

from academic_chat import AcademicChatAssistant


def demo():
    """演示学术助手功能"""
    
    assistant = AcademicChatAssistant()
    
    # 演示问题列表
    questions = [
        "2024年机器学习领域有哪些重要论文？",
        "查询论文W2626778328的详细信息",
        "总结一下GPT-4相关的研究",
        "深度学习领域的研究趋势是什么？"
    ]
    
    print("\n" + "="*80)
    print("🎓 学术助手功能演示")
    print("="*80 + "\n")
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"演示 {i}/{len(questions)}")
        print(f"{'='*80}\n")
        
        assistant.ask(question)
        
        if i < len(questions):
            input("\n按回车键继续下一个演示...")
    
    print("\n" + "="*80)
    print("🎉 演示完成！")
    print("="*80)
    print("\n💡 您现在可以运行以下命令启动交互式对话：")
    print("   python academic_chat.py")
    print("\n然后就可以直接用自然语言提问了！")


if __name__ == "__main__":
    demo()
