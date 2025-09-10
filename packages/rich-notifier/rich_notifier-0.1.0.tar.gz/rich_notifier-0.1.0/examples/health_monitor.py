#!/usr/bin/env python3
"""
网站健康检查场景演示

模拟系统监控和健康检查的完整流程
"""

import time
import random
from rich_notifier import Notifier

def check_system_resources():
    """检查系统资源使用情况"""
    Notifier.info("💻 开始检查系统资源...")
    time.sleep(1)
    
    # 模拟各种资源检查
    cpu_usage = random.uniform(15, 85)
    memory_usage = random.uniform(40, 90)
    disk_usage = random.uniform(30, 95)
    
    Notifier.info("检查CPU使用率...")
    time.sleep(0.5)
    
    Notifier.info("检查内存使用情况...")
    time.sleep(0.5)
    
    Notifier.info("检查磁盘空间...")
    time.sleep(0.5)
    
    # 根据使用率给出不同的提示
    if cpu_usage > 80:
        Notifier.warning(f"⚠️ CPU使用率较高: {cpu_usage:.1f}%")
    elif cpu_usage > 90:
        Notifier.error(f"🔥 CPU使用率过高: {cpu_usage:.1f}%")
    else:
        Notifier.success(f"✅ CPU使用正常: {cpu_usage:.1f}%")
    
    if memory_usage > 85:
        Notifier.warning(f"⚠️ 内存使用率较高: {memory_usage:.1f}%")
    else:
        Notifier.success(f"✅ 内存使用正常: {memory_usage:.1f}%")
    
    if disk_usage > 90:
        Notifier.error(f"🔥 磁盘空间不足: {disk_usage:.1f}%")
    elif disk_usage > 80:
        Notifier.warning(f"⚠️ 磁盘空间告急: {disk_usage:.1f}%")
    else:
        Notifier.success(f"✅ 磁盘空间充足: {disk_usage:.1f}%")
    
    system_status = {
        "CPU使用率": f"{cpu_usage:.1f}%",
        "内存使用率": f"{memory_usage:.1f}%", 
        "磁盘使用率": f"{disk_usage:.1f}%",
        "运行时间": "3天 12小时 45分钟",
        "负载均衡": f"{random.uniform(0.5, 2.1):.2f}",
        "系统温度": f"{random.randint(45, 68)}°C"
    }
    
    # 根据整体状况选择颜色
    if cpu_usage > 80 or memory_usage > 85 or disk_usage > 90:
        border_color = "red"
        status = "🔥 需要关注"
    elif cpu_usage > 70 or memory_usage > 75 or disk_usage > 80:
        border_color = "yellow" 
        status = "⚠️ 轻微警告"
    else:
        border_color = "green"
        status = "✅ 运行良好"
    
    system_status["整体状态"] = status
    Notifier.show_panel("💻 系统资源状态", system_status, border_color=border_color)
    
    return cpu_usage, memory_usage, disk_usage

def check_network_connectivity():
    """检查网络连通性"""
    Notifier.info("🌐 开始检查网络连通性...")
    
    endpoints = [
        ("内部API", "https://api.internal.com"),
        ("外部服务", "https://api.external.com"),
        ("数据库", "db.example.com:5432"),
        ("缓存服务", "redis.example.com:6379"),
        ("CDN节点", "https://cdn.example.com")
    ]
    
    results = {}
    
    for name, endpoint in endpoints:
        Notifier.info(f"检查 {name}: {endpoint}")
        time.sleep(random.uniform(0.3, 1.2))
        
        # 模拟不同的连接结果
        success_rate = random.choice([0.9, 0.9, 0.9, 0.7, 0.5])  # 大部分情况成功
        
        if random.random() < success_rate:
            response_time = random.uniform(10, 200)
            Notifier.success(f"✅ {name} 连接正常 ({response_time:.0f}ms)")
            results[name] = {
                "状态": "🟢 正常",
                "响应时间": f"{response_time:.0f}ms",
                "可用性": "100%"
            }
        else:
            if random.choice([True, False]):
                Notifier.warning(f"⚠️ {name} 响应超时")
                results[name] = {
                    "状态": "🟡 超时",
                    "响应时间": "> 5000ms",
                    "可用性": "0%"
                }
            else:
                Notifier.error(f"❌ {name} 连接失败")
                results[name] = {
                    "状态": "🔴 失败", 
                    "响应时间": "N/A",
                    "可用性": "0%"
                }
    
    # 计算整体网络状态
    normal_count = sum(1 for r in results.values() if "正常" in r["状态"])
    total_count = len(results)
    
    network_summary = {
        "检查节点": f"{total_count} 个",
        "正常节点": f"{normal_count} 个",
        "异常节点": f"{total_count - normal_count} 个",
        "整体可用性": f"{(normal_count/total_count)*100:.1f}%",
        "平均响应": f"{random.randint(50, 150)}ms",
        "网络质量": "🟢 良好" if normal_count >= total_count * 0.8 else "🟡 一般"
    }
    
    color = "green" if normal_count >= total_count * 0.8 else "yellow" if normal_count >= total_count * 0.6 else "red"
    Notifier.show_panel("🌐 网络连通性检查", network_summary, border_color=color)
    
    return results

def check_services():
    """检查各项服务状态"""
    Notifier.info("🔧 开始检查服务状态...")
    
    services = [
        "Web服务器 (Nginx)",
        "应用服务器 (Node.js)",
        "数据库服务 (PostgreSQL)", 
        "缓存服务 (Redis)",
        "消息队列 (RabbitMQ)",
        "文件存储 (MinIO)"
    ]
    
    service_results = {}
    
    for service in services:
        Notifier.info(f"检查 {service}...")
        time.sleep(random.uniform(0.5, 1.5))
        
        # 模拟服务状态
        status_chance = random.random()
        
        if status_chance > 0.15:  # 85% 正常
            uptime = random.randint(1, 30)
            memory_usage = random.uniform(100, 800)
            Notifier.success(f"✅ {service} 运行正常")
            service_results[service] = {
                "状态": "🟢 运行中",
                "运行时间": f"{uptime}天",
                "内存使用": f"{memory_usage:.0f}MB",
                "健康度": "100%"
            }
        elif status_chance > 0.05:  # 10% 警告
            Notifier.warning(f"⚠️ {service} 性能下降")
            service_results[service] = {
                "状态": "🟡 警告",
                "运行时间": f"{random.randint(1, 10)}天",
                "内存使用": f"{random.uniform(800, 1200):.0f}MB",
                "健康度": "70%"
            }
        else:  # 5% 错误
            Notifier.error(f"❌ {service} 服务异常")
            service_results[service] = {
                "状态": "🔴 异常",
                "运行时间": "N/A",
                "内存使用": "N/A", 
                "健康度": "0%"
            }
    
    # 服务状态汇总
    normal_services = sum(1 for r in service_results.values() if "运行中" in r["状态"])
    warning_services = sum(1 for r in service_results.values() if "警告" in r["状态"])
    error_services = sum(1 for r in service_results.values() if "异常" in r["状态"])
    
    services_summary = {
        "总服务数": f"{len(services)} 个",
        "正常运行": f"{normal_services} 个",
        "警告状态": f"{warning_services} 个", 
        "异常服务": f"{error_services} 个",
        "服务可用性": f"{(normal_services/len(services))*100:.1f}%",
        "整体状态": "🟢 健康" if error_services == 0 else "🟡 部分异常" if error_services < 2 else "🔴 严重"
    }
    
    color = "green" if error_services == 0 else "yellow" if error_services < 2 else "red"
    Notifier.show_panel("🔧 服务状态检查", services_summary, border_color=color)
    
    return service_results

def check_security():
    """安全状态检查"""
    Notifier.info("🔐 开始安全状态检查...")
    time.sleep(1)
    
    Notifier.info("检查SSL证书有效性...")
    time.sleep(0.8)
    
    Notifier.info("扫描端口安全状态...")
    time.sleep(1.2)
    
    Notifier.info("检查防火墙规则...")
    time.sleep(0.6)
    
    Notifier.info("分析访问日志...")
    time.sleep(1)
    
    # 模拟安全检查结果
    ssl_days_left = random.randint(15, 200)
    failed_logins = random.randint(0, 25)
    blocked_ips = random.randint(0, 15)
    
    security_status = {
        "SSL证书": f"有效 (剩余{ssl_days_left}天)",
        "防火墙": "🟢 活跃",
        "入侵检测": "🟢 正常", 
        "失败登录": f"{failed_logins} 次 (24小时)",
        "封禁IP": f"{blocked_ips} 个",
        "安全等级": "🛡️ 高"
    }
    
    # 根据安全指标判断状态
    if ssl_days_left < 30:
        Notifier.warning(f"⚠️ SSL证书即将过期 (剩余{ssl_days_left}天)")
        color = "yellow"
    elif failed_logins > 20:
        Notifier.warning("⚠️ 检测到异常登录尝试")
        color = "yellow"
    else:
        Notifier.success("✅ 安全状态良好")
        color = "green"
    
    Notifier.show_panel("🔐 安全状态检查", security_status, border_color=color)

def generate_health_report():
    """生成健康检查报告"""
    Notifier.info("📊 正在生成健康检查报告...")
    time.sleep(1.5)
    
    Notifier.success("📋 健康检查报告生成完成")
    
    report_details = {
        "报告时间": "2025-01-15 14:45:23",
        "检查项目": "16 项",
        "异常项目": f"{random.randint(0, 3)} 项",
        "总体评分": f"{random.randint(85, 98)}/100",
        "报告文件": "health_report_20250115.pdf",
        "下次检查": "1小时后"
    }
    Notifier.show_panel("📋 健康报告", report_details, border_color="blue")

def main():
    """主函数 - 完整的健康检查流程"""
    print("🏥 系统健康监控演示")
    print("=" * 50)
    
    try:
        # 检查1：系统资源
        cpu, memory, disk = check_system_resources()
        print("\n" + "-"*40 + "\n")
        
        # 检查2：网络连通性
        network_results = check_network_connectivity() 
        print("\n" + "-"*40 + "\n")
        
        # 检查3：服务状态
        service_results = check_services()
        print("\n" + "-"*40 + "\n")
        
        # 检查4：安全状态
        check_security()
        print("\n" + "-"*40 + "\n")
        
        # 生成报告
        generate_health_report()
        print("\n" + "="*50 + "\n")
        
        # 健康检查总结
        Notifier.success("🎉 系统健康检查完成！")
        
        # 计算综合评估
        issues = 0
        if cpu > 80: issues += 1
        if memory > 85: issues += 1  
        if disk > 90: issues += 1
        
        network_issues = sum(1 for r in network_results.values() if "正常" not in r["状态"])
        service_issues = sum(1 for r in service_results.values() if "运行中" not in r["状态"])
        
        total_issues = issues + network_issues + service_issues
        
        if total_issues == 0:
            overall_status = "[bold green]🏆 优秀[/bold green]"
            color = "green"
        elif total_issues <= 2:
            overall_status = "[bold yellow]⚠️ 良好[/bold yellow]"
            color = "yellow"
        else:
            overall_status = "[bold red]🔥 需要关注[/bold red]"
            color = "red"
        
        final_summary = {
            "检查耗时": f"{random.randint(3, 8)} 分钟",
            "检查项目": "16 项",
            "发现问题": f"{total_issues} 个",
            "系统可用性": f"{100 - total_issues*5:.1f}%",
            "整体状态": overall_status,
            "建议": "继续监控" if total_issues <= 1 else "需要处理部分问题"
        }
        Notifier.show_panel("🏥 健康检查总结", final_summary, border_color=color)
        
    except KeyboardInterrupt:
        Notifier.warning("⏹️ 健康检查被用户中断")
    except Exception as e:
        Notifier.error(f"💥 健康检查过程出错: {e}")

if __name__ == "__main__":
    main()