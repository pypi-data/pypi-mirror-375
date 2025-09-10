#!/usr/bin/env python3
"""
Rich Notifier 综合功能演示

展示所有功能的综合示例，包括各种颜色、样式和使用场景
"""

import time
import random
from rich_notifier import Notifier

def demo_basic_messages():
    """演示基本消息类型"""
    print("🎨 基本消息类型演示")
    print("-" * 30)
    
    Notifier.info("这是普通信息消息")
    time.sleep(0.5)
    
    Notifier.success("这是成功消息 - 绿色加粗")
    time.sleep(0.5)
    
    Notifier.warning("这是警告消息 - 黄色加粗")
    time.sleep(0.5)
    
    Notifier.error("这是错误消息 - 红色加粗")
    time.sleep(0.5)

def demo_panels():
    """演示不同颜色和样式的面板"""
    print("\n📊 信息面板演示")
    print("-" * 30)
    
    # 绿色面板 - 成功/完成
    success_data = {
        "任务状态": "[green]✅ 已完成[/green]",
        "完成时间": "2025-01-15 14:30:25",
        "处理记录": "1,234 条",
        "成功率": "100%"
    }
    Notifier.show_panel("🎉 任务完成", success_data, border_color="green")
    time.sleep(1)
    
    # 蓝色面板 - 信息展示
    info_data = {
        "服务名称": "数据处理服务",
        "版本": "v2.1.0",
        "运行时间": "3天 2小时 15分钟",
        "内存使用": "512 MB",
        "CPU使用": "15.3%"
    }
    Notifier.show_panel("💻 系统状态", info_data, border_color="blue")
    time.sleep(1)
    
    # 黄色面板 - 警告信息
    warning_data = {
        "警告类型": "资源使用率高",
        "磁盘使用": "87%",
        "内存使用": "92%",
        "建议操作": "清理临时文件",
        "监控级别": "[yellow]⚠️ 中等[/yellow]"
    }
    Notifier.show_panel("⚠️ 系统警告", warning_data, border_color="yellow")
    time.sleep(1)
    
    # 红色面板 - 错误信息
    error_data = {
        "错误代码": "DB_CONNECTION_FAILED",
        "错误时间": "2025-01-15 14:32:10",
        "影响范围": "用户认证模块",
        "预计修复": "30分钟内",
        "状态": "[red]🔥 紧急[/red]"
    }
    Notifier.show_panel("🚨 系统错误", error_data, border_color="red")
    time.sleep(1)
    
    # 紫色面板 - 特殊信息
    special_data = {
        "报告类型": "月度分析报告",
        "生成时间": "15 分钟",
        "图表数量": "12 个",
        "页数": "45 页",
        "格式": "PDF + Excel"
    }
    Notifier.show_panel("📋 报告生成", special_data, border_color="purple")
    time.sleep(1)
    
    # 青色面板 - 网络/API相关
    network_data = {
        "API端点": "https://api.example.com/v2",
        "响应时间": "245ms",
        "状态码": "200 OK",
        "数据传输": "2.3 MB",
        "连接质量": "[cyan]🌐 优秀[/cyan]"
    }
    Notifier.show_panel("🔗 网络状态", network_data, border_color="cyan")
    time.sleep(1)

def demo_real_world_scenario():
    """演示真实世界的使用场景"""
    print("\n🚀 真实场景模拟")
    print("-" * 30)
    
    # 模拟应用启动过程
    Notifier.info("🔄 正在启动应用...")
    time.sleep(0.8)
    
    Notifier.info("📝 加载配置文件...")
    time.sleep(0.5)
    
    Notifier.info("🔌 连接数据库...")
    time.sleep(1)
    
    Notifier.success("✅ 数据库连接成功")
    
    # 显示数据库连接信息
    db_info = {
        "数据库类型": "PostgreSQL 13",
        "连接池": "20 连接",
        "响应时间": "12ms",
        "状态": "[green]健康[/green]",
        "最后检查": "刚刚"
    }
    Notifier.show_panel("🗄️ 数据库状态", db_info, border_color="green")
    time.sleep(1)
    
    Notifier.info("🌐 启动Web服务...")
    time.sleep(0.8)
    
    Notifier.success("🎯 应用启动完成")
    
    # 显示应用启动摘要
    startup_summary = {
        "启动时间": "3.2 秒",
        "加载模块": "15 个",
        "监听端口": "8080",
        "工作进程": "4 个",
        "准备状态": "[bold green]🟢 就绪[/bold green]"
    }
    Notifier.show_panel("🚀 启动摘要", startup_summary, border_color="blue")

def demo_progress_simulation():
    """模拟进度处理场景"""
    print("\n⏳ 处理进度模拟")
    print("-" * 30)
    
    tasks = [
        "初始化环境",
        "加载数据源", 
        "验证数据格式",
        "执行数据清洗",
        "计算统计指标",
        "生成报告",
        "保存结果"
    ]
    
    for i, task in enumerate(tasks, 1):
        Notifier.info(f"📋 步骤 {i}/{len(tasks)}: {task}")
        time.sleep(random.uniform(0.5, 1.5))
        
        # 偶尔显示警告
        if random.choice([True, False, False, False]):
            Notifier.warning(f"⚠️ {task}过程中发现次要问题，已自动处理")
            time.sleep(0.5)
        
        if i < len(tasks):
            Notifier.success(f"✅ {task} 完成")
    
    # 最终结果
    Notifier.success("🎊 所有任务执行完毕！")
    
    final_results = {
        "总任务数": f"{len(tasks)} 个",
        "成功任务": f"{len(tasks)} 个",
        "失败任务": "0 个",
        "总耗时": "8.7 秒",
        "平均速度": "0.8 任务/秒",
        "整体状态": "[bold green]🏆 完美完成[/bold green]"
    }
    Notifier.show_panel("📊 执行总结", final_results, border_color="gold")

def main():
    """主函数"""
    print("🎪 Rich Notifier 综合功能演示")
    print("=" * 50)
    print()
    
    try:
        # 基本消息演示
        demo_basic_messages()
        
        # 面板演示
        demo_panels()
        
        # 真实场景演示
        demo_real_world_scenario()
        
        # 进度处理演示
        demo_progress_simulation()
        
        print("\n" + "=" * 50)
        print("🎉 演示完成！Rich Notifier 让你的终端输出更加美观！")
        
    except KeyboardInterrupt:
        print("\n")
        Notifier.warning("⏹️ 演示被用户中断")
    except Exception as e:
        Notifier.error(f"💥 演示过程出错: {e}")

if __name__ == "__main__":
    main()