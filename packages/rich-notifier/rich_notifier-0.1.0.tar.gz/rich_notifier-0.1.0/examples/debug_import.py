#!/usr/bin/env python3
"""
调试模块导入问题
"""

import sys
import os
import inspect

# 确保路径正确
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("=== 调试信息 ===")
print(f"当前工作目录: {os.getcwd()}")
print(f"脚本目录: {os.path.dirname(__file__)}")
print(f"添加的路径: {os.path.join(os.path.dirname(__file__), '..')}")
print()

# 导入模块
from rich_notifier import Notifier

# 检查模块文件位置
print("=== 模块信息 ===")
print(f"Notifier 类来源: {inspect.getfile(Notifier)}")
print(f"success 方法代码:")

# 获取 success 方法的源码
try:
    source = inspect.getsource(Notifier.success)
    print(source)
except Exception as e:
    print(f"无法获取源码: {e}")

print("\n=== 直接测试 ===")
print("测试 success 方法:")
Notifier.success("测试成功消息 - 应该有绿色背景")

print("\n测试 warning 方法:")
Notifier.warning("测试警告消息 - 应该有下划线")

# 检查是否有 __pycache__ 文件
pycache_dir = os.path.join(os.path.dirname(__file__), '..', 'rich_notifier', '__pycache__')
if os.path.exists(pycache_dir):
    print(f"\n=== 发现 __pycache__ 目录 ===")
    print(f"位置: {pycache_dir}")
    print("缓存文件:")
    for file in os.listdir(pycache_dir):
        print(f"  - {file}")
else:
    print("\n未发现 __pycache__ 目录")