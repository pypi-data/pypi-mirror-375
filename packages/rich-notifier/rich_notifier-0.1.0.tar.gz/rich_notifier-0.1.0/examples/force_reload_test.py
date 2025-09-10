#!/usr/bin/env python3
"""
强制重新加载模块测试
"""

import sys
import os
import importlib

# 确保路径正确
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 清除可能的缓存模块
modules_to_remove = [name for name in sys.modules.keys() if 'rich_notifier' in name]
for module in modules_to_remove:
    print(f"移除缓存模块: {module}")
    del sys.modules[module]

# 重新导入
from rich_notifier import Notifier

print("=== 强制重新加载后的测试 ===")
print("1. 普通信息:")
Notifier.info("这是一条普通信息")

print("\n2. 成功消息 (应该有绿色背景):")
Notifier.success("这是一条成功消息！")

print("\n3. 警告消息 (应该有下划线):")
Notifier.warning("这是一条警告消息")

print("\n4. 错误消息 (应该是红色加粗):")
Notifier.error("这是一条错误消息")