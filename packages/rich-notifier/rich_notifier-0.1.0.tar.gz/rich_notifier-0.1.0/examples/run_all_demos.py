#!/usr/bin/env python3
"""
运行所有 Rich Notifier 演示脚本

这个脚本会依次运行所有的演示示例，展示 Rich Notifier 的完整功能
"""

import sys
import subprocess
import time
from rich_notifier import Notifier

def run_demo(script_name, description):
    """运行指定的演示脚本"""
    try:
        Notifier.info(f"🎬 准备运行: {description}")
        Notifier.info(f"📜 脚本文件: {script_name}")
        print("\n" + "="*60)
        print(f"开始运行: {script_name}")
        print("="*60 + "\n")
        
        # 运行脚本
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True)
        
        print("\n" + "="*60)
        
        if result.returncode == 0:
            Notifier.success(f"✅ {description} - 演示完成")
            return True
        else:
            Notifier.error(f"❌ {description} - 执行出错")
            return False
            
    except KeyboardInterrupt:
        Notifier.warning(f"⏹️ {description} - 被用户中断")
        return False
    except Exception as e:
        Notifier.error(f"💥 {description} - 执行异常: {e}")
        return False

def main():
    """主函数"""
    print("🎪 Rich Notifier 完整演示")
    print("=" * 60)
    print()
    
    Notifier.info("🚀 准备运行所有演示脚本...")
    print()
    
    # 定义所有演示脚本
    demos = [
        ("contrast_demo.py", "效果对比演示 - 推荐优先观看"),
        ("basic_usage.py", "基础功能演示"),
        ("data_processing.py", "数据处理场景"),
        ("api_client.py", "API客户端场景"),
        ("ml_training.py", "机器学习训练"),
        ("batch_processing.py", "文件批处理"),
        ("health_monitor.py", "系统健康检查"),
        ("scheduler_demo.py", "定时任务调度"),
        ("comprehensive_demo.py", "综合功能展示")
    ]
    
    results = []
    
    try:
        for i, (script, description) in enumerate(demos, 1):
            print(f"\n🎭 演示 {i}/{len(demos)}: {description}")
            print("-" * 50)
            
            # 询问用户是否继续
            try:
                response = input(f"按 Enter 键开始运行 '{description}' (输入 's' 跳过, 'q' 退出): ").strip().lower()
                
                if response == 'q':
                    Notifier.info("👋 用户选择退出演示")
                    break
                elif response == 's':
                    Notifier.info(f"⏭️ 跳过: {description}")
                    results.append(None)
                    continue
                    
            except (EOFError, KeyboardInterrupt):
                Notifier.warning("⏹️ 用户中断演示")
                break
            
            # 运行演示
            success = run_demo(script, description)
            results.append(success)
            
            print("\n" + "-" * 50)
            
            # 演示间隔
            if i < len(demos):
                print("⏳ 3秒后继续下一个演示...")
                time.sleep(3)
        
        # 显示总结
        print("\n" + "=" * 60)
        Notifier.info("📊 正在生成演示总结...")
        time.sleep(1)
        
        completed = sum(1 for r in results if r is not None)
        successful = sum(1 for r in results if r is True)
        skipped = sum(1 for r in results if r is None)
        failed = sum(1 for r in results if r is False)
        
        summary = {
            "总演示数": f"{len(demos)} 个",
            "已运行": f"{completed} 个", 
            "成功完成": f"{successful} 个",
            "跳过": f"{skipped} 个",
            "执行失败": f"{failed} 个",
            "完成率": f"{(successful/completed)*100:.1f}%" if completed > 0 else "0%"
        }
        
        if failed == 0 and completed > 0:
            Notifier.success("🎉 所有演示都成功完成！")
            color = "green"
            status = "[bold green]🏆 完美演示[/bold green]"
        elif failed <= 1:
            Notifier.success("✅ 演示基本完成")
            color = "yellow" 
            status = "[bold yellow]⚠️ 良好演示[/bold yellow]"
        else:
            Notifier.warning("⚠️ 演示完成，但有多项失败")
            color = "red"
            status = "[bold red]🔥 部分失败[/bold red]"
        
        summary["整体状态"] = status
        
        Notifier.show_panel("🎪 演示总结", summary, border_color=color)
        
        print("\n🎊 感谢您体验 Rich Notifier！")
        print("🔗 获取更多信息: https://github.com/yourusername/rich-notifier")
        
    except KeyboardInterrupt:
        print("\n")
        Notifier.warning("⏹️ 演示被用户中断")
    except Exception as e:
        Notifier.error(f"💥 演示脚本执行出错: {e}")

if __name__ == "__main__":
    main()