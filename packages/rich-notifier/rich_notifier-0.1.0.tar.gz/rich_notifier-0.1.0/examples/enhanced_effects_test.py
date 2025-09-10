#!/usr/bin/env python3
"""
增强视觉效果测试脚本
展示修改后的 rich-notifier 新样式效果
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rich_notifier import Notifier
from rich import print

def test_enhanced_effects():
    print("🎨 Rich Notifier 增强视觉效果演示\n")
    
    print("=" * 60)
    print("📢 修改后的消息样式效果:")
    print("=" * 60)
    
    print("\n1. 普通信息 (保持不变):")
    Notifier.info("这是一条普通信息消息")
    
    print("\n2. 成功消息 (绿色背景):")
    Notifier.success("这是一条成功消息！")
    Notifier.success("文件保存成功")
    Notifier.success("数据处理完成")
    
    print("\n3. 警告消息 (黄色下划线):")
    Notifier.warning("这是一条警告消息")
    Notifier.warning("配置文件缺失，使用默认设置")
    Notifier.warning("网络连接较慢")
    
    print("\n4. 错误消息 (红色加粗):")
    Notifier.error("这是一条错误消息")
    Notifier.error("文件未找到")
    Notifier.error("连接失败")
    
    print("\n" + "=" * 60)
    print("🎯 样式说明:")
    print("  ✓ 普通消息: 默认颜色，无特殊样式")
    print("  ✓ 成功消息: 黑字绿底，突出显示成功状态")
    print("  ✓ 警告消息: 黄色下划线，提醒注意")
    print("  ✓ 错误消息: 红色加粗，强调错误")
    print("=" * 60)

if __name__ == "__main__":
    test_enhanced_effects()