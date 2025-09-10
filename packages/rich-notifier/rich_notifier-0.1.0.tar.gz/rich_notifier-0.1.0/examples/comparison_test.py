#!/usr/bin/env python3
"""
对比测试：原版 vs PowerShell 兼容版
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rich_notifier import Notifier as OriginalNotifier
from rich_notifier.powershell_compatible import PSNotifier

def comparison_test():
    print("=== 原版 Notifier ===")
    OriginalNotifier.info("这是一条普通信息")
    OriginalNotifier.success("这是一条成功消息！")
    OriginalNotifier.warning("这是一条警告消息")
    OriginalNotifier.error("这是一条错误消息")
    
    print("\n=== PowerShell 兼容版 ===")
    PSNotifier.info("这是一条普通信息")
    PSNotifier.success("这是一条成功消息！")
    PSNotifier.warning("这是一条警告消息")
    PSNotifier.error("这是一条错误消息")
    
    print("\n如果上面的 PowerShell 兼容版中 SUCCESS 和 WARNING 颜色不同，")
    print("说明问题已解决！")

if __name__ == "__main__":
    comparison_test()