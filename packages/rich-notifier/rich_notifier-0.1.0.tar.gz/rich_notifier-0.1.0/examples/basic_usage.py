#!/usr/bin/env python3
"""
Rich Notifier 基本使用示例

演示所有基本的通知功能
"""

import time
from rich_notifier import Notifier

def main():
    print("🎨 Rich Notifier 基本使用演示\n")
    
    # 基本消息类型演示
    print("📢 基本消息类型:")
    Notifier.info("这是一条普通信息")
    time.sleep(1)
    
    Notifier.success("这是一条成功消息！")
    time.sleep(1)
    
    Notifier.warning("这是一条警告消息")
    time.sleep(1)
    
    Notifier.error("这是一条错误消息")
    time.sleep(1)
    
    print("\n" + "="*50 + "\n")
    
    # 信息面板演示
    print("📊 信息面板演示:")
    
    # 系统信息面板
    system_info = {
        "操作系统": "Windows 11",
        "Python版本": "3.11.0",
        "内存使用": "2.1 GB / 16 GB",
        "磁盘空间": "256 GB 可用"
    }
    Notifier.show_panel("💻 系统信息", system_info, border_color="cyan")
    time.sleep(2)
    
    # 用户信息面板
    user_info = {
        "用户名": "开发者",
        "登录时间": "2025-01-15 14:30:00",
        "会话状态": "活跃",
        "权限级别": "管理员"
    }
    Notifier.show_panel("👤 用户会话", user_info, border_color="blue")
    time.sleep(2)
    
    # 任务完成面板
    task_summary = {
        "任务名称": "数据处理",
        "开始时间": "14:25:00",
        "结束时间": "14:30:00",
        "处理记录": "1,234 条",
        "成功率": "99.8%",
        "状态": "[bold green]✓ 完成[/bold green]"
    }
    Notifier.show_panel("🎉 任务完成", task_summary, border_color="green")
    
    print("\n演示完成！ 🎊")

if __name__ == "__main__":
    main()