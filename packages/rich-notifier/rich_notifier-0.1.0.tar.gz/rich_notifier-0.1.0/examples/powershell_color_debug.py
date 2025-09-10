#!/usr/bin/env python3
"""
PowerShell 颜色显示调试脚本
"""

import os
import sys
from rich import print
from rich.console import Console

def debug_powershell_colors():
    console = Console()
    
    print("=== 环境信息 ===")
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {os.name}")
    print(f"TERM环境变量: {os.environ.get('TERM', '未设置')}")
    print(f"COLORTERM环境变量: {os.environ.get('COLORTERM', '未设置')}")
    print(f"FORCE_COLOR环境变量: {os.environ.get('FORCE_COLOR', '未设置')}")
    print()
    
    print("=== Rich 控制台信息 ===")
    print(f"是否为终端: {console.is_terminal}")
    print(f"颜色系统: {console.color_system}")
    print(f"编码: {console.encoding}")
    print(f"宽度: {console.width}")
    print(f"高度: {console.height}")
    print()
    
    print("=== 基础颜色测试 ===")
    colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    for color in colors:
        print(f"[{color}]这是 {color} 颜色[/{color}]")
    print()
    
    print("=== 加粗颜色测试 ===")
    for color in colors:
        print(f"[bold {color}]这是加粗 {color} 颜色[/bold {color}]")
    print()
    
    print("=== 具体问题测试 ===")
    print("SUCCESS (应该是绿色):")
    print("[bold green]这是一条成功消息！[/bold green]")
    print()
    print("WARNING (应该是黄色):")  
    print("[bold yellow]这是一条警告消息[/bold yellow]")
    print()
    print("如果上面两行颜色相同，说明 PowerShell 的黄色被映射为其他颜色")

if __name__ == "__main__":
    debug_powershell_colors()