#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试对话助手
"""

from academic_chat import AcademicChatAssistant


def quick_test():
    """快速测试"""
    
    assistant = AcademicChatAssistant()
    
    # 测试1: 搜索论文
    print("\n" + "="*80)
    print("测试1: 搜索机器学习论文")
    print("="*80)
    assistant.ask("2024年machine learning有哪些重要论文？")
    
    # 测试2: 查询论文详情
    print("\n" + "="*80)
    print("测试2: 查询论文详情")
    print("="*80)
    assistant.ask("查询论文W2626778328的详细信息")


if __name__ == "__main__":
    quick_test()
