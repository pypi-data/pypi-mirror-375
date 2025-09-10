#!/usr/bin/env python3
"""
详细调试脚本 - 找出导入问题
"""

import sys
import os
import inspect

print("=== 调试 Python 导入路径 ===")
print("当前工作目录:", os.getcwd())
print("Python 搜索路径:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")
print()

# 清除所有相关模块
modules_to_remove = [name for name in sys.modules.keys() if 'rich_notifier' in name]
for module in modules_to_remove:
    print(f"清除模块: {module}")
    del sys.modules[module]

# 手动添加路径
current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.insert(0, parent_dir)
print(f"添加路径到搜索开头: {parent_dir}")
print()

# 导入并检查
print("=== 导入模块 ===")
from rich_notifier import Notifier

# 获取实际文件位置
try:
    module_file = inspect.getfile(Notifier)
    print(f"实际导入的文件: {module_file}")
except:
    print("无法获取模块文件位置")

# 获取 success 方法源码
print("\n=== success 方法源码 ===")
try:
    source_lines = inspect.getsourcelines(Notifier.success)
    for i, line in enumerate(source_lines[0], source_lines[1]):
        print(f"{i:3}: {line.rstrip()}")
except Exception as e:
    print(f"无法获取源码: {e}")

# 直接检查方法内容
print("\n=== 直接测试方法 ===")

# 创建一个简单的测试函数来查看实际输出
import io
from contextlib import redirect_stdout

with redirect_stdout(io.StringIO()) as f:
    Notifier.success("测试")
output = f.getvalue()

print(f"success 方法实际输出: {repr(output)}")

# 测试其他可能的文件
print("\n=== 检查所有可能的 rich_notifier.py 文件 ===")
possible_files = [
    r"C:\My_project\alpha\rich_notifier.py",
    r"C:\My_project\alpha\rich-notifier\rich_notifier\rich_notifier.py", 
    r"C:\My_project\alpha\rich-notifier\examples\rich_notifier.py"
]

for file_path in possible_files:
    if os.path.exists(file_path):
        print(f"\n文件: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[19:25], 20):  # 查看第20-25行
                    print(f"{i:3}: {line.rstrip()}")
        except Exception as e:
            print(f"  错误: {e}")
    else:
        print(f"文件不存在: {file_path}")