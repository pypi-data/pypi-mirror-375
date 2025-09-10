#!/usr/bin/env python3
"""
PowerShell 颜色解决方案测试
"""

from rich import print

def test_color_solutions():
    print("=== 问题重现 ===")
    print("当前 Notifier 的实现:")
    print("[bold green]SUCCESS: 这是一条成功消息！[/bold green]")
    print("[bold yellow]WARNING: 这是一条警告消息[/bold yellow]")
    print()
    
    print("=== 解决方案1: 去掉加粗，保留颜色 ===")
    print("[green]SUCCESS: 这是一条成功消息！[/green]")
    print("[yellow]WARNING: 这是一条警告消息[/yellow]")
    print()
    
    print("=== 解决方案2: 使用不同的颜色组合 ===")
    print("[bright_green]SUCCESS: 这是一条成功消息！[/bright_green]")
    print("[bright_yellow]WARNING: 这是一条警告消息[/bright_yellow]")
    print()
    
    print("=== 解决方案3: 使用背景色 ===")
    print("[black on green]SUCCESS: 这是一条成功消息！[/black on green]")
    print("[black on yellow]WARNING: 这是一条警告消息[/black on yellow]")
    print()
    
    print("=== 解决方案4: 使用符号区分 ===")
    print("[green]✓ SUCCESS: 这是一条成功消息！[/green]")
    print("[yellow]⚠ WARNING: 这是一条警告消息[/yellow]")
    print()
    
    print("=== 解决方案5: 使用RGB颜色 ===")
    print("[rgb(0,255,0)]SUCCESS: 这是一条成功消息！[/rgb(0,255,0)]")
    print("[rgb(255,255,0)]WARNING: 这是一条警告消息[/rgb(255,255,0)]")
    print()
    
    print("=== 解决方案6: 混合样式 ===")
    print("[italic green]SUCCESS: 这是一条成功消息！[/italic green]")
    print("[underline yellow]WARNING: 这是一条警告消息[/underline yellow]")

if __name__ == "__main__":
    test_color_solutions()