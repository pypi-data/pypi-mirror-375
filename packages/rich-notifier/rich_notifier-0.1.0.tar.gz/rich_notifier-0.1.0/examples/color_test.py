#!/usr/bin/env python3
"""
颜色显示测试脚本
用于诊断终端是否支持 Rich 颜色显示
"""

from rich import print
from rich.console import Console
from rich_notifier import Notifier

def test_colors():
    console = Console()
    
    print("=== 终端颜色支持检测 ===")
    print(f"终端支持颜色: {console.is_terminal}")
    print(f"颜色系统: {console.color_system}")
    print(f"编码: {console.encoding}")
    print()
    
    print("=== Rich 原生颜色测试 ===")
    print("[bold red]这应该是红色加粗[/bold red]")
    print("[bold green]这应该是绿色加粗[/bold green]")
    print("[bold yellow]这应该是黄色加粗[/bold yellow]")
    print("[bold blue]这应该是蓝色加粗[/bold blue]")
    print()
    
    print("=== Notifier 颜色测试 ===")
    Notifier.info("这是普通信息 (应该是默认颜色)")
    Notifier.success("这是成功消息 (应该是绿色)")
    Notifier.warning("这是警告消息 (应该是黄色)")
    Notifier.error("这是错误消息 (应该是红色)")
    print()
    
    print("=== 标准 print 对比 ===")
    print("这是普通 print 输出")

if __name__ == "__main__":
    test_colors()