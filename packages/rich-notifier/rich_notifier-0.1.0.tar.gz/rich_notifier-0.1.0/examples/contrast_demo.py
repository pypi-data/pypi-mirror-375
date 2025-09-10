#!/usr/bin/env python3
"""
对比演示：传统输出 vs Rich Notifier 输出
场景：机器学习超参数调优过程
展示在大量调参日志中，如何突出关键的最优参数发现和训练结果
"""

import time
import random
from rich_notifier import Notifier

def simulate_traditional_output():
    """传统方式：使用 print() 输出大量调参日志"""
    print("=" * 60)
    print("传统输出方式（使用 print）- 机器学习超参数调优")
    print("=" * 60)
    
    # 模拟大量超参数调优日志输出
    logs = [
        "2025-01-15 14:23:01 INFO: Loading dataset: CIFAR-10 (50000 training, 10000 test)",
        "2025-01-15 14:23:01 DEBUG: Initializing hyperparameter search space",
        "2025-01-15 14:23:02 INFO: Search space: lr=[0.0001-0.1], batch_size=[16,32,64,128], dropout=[0.1-0.5]",
        "2025-01-15 14:23:02 DEBUG: Starting hyperparameter optimization with 50 trials",
        "2025-01-15 14:23:03 INFO: Trial 1/50: lr=0.001, batch_size=32, dropout=0.2, epochs=20",
        "2025-01-15 14:23:04 DEBUG: Building CNN model with 3 conv layers", 
        "2025-01-15 14:23:05 DEBUG: Model parameters: 2.3M trainable",
        "2025-01-15 14:23:06 DEBUG: Starting training... Epoch 1/20",
        "2025-01-15 14:23:07 DEBUG: Epoch 1 - train_loss: 2.234, train_acc: 0.189",
        "2025-01-15 14:23:08 DEBUG: Epoch 2 - train_loss: 1.987, train_acc: 0.245",
        "2025-01-15 14:23:09 DEBUG: Epoch 3 - train_loss: 1.756, train_acc: 0.342",
        "2025-01-15 14:23:10 DEBUG: Early stopping triggered - no improvement for 5 epochs",
        "2025-01-15 14:23:11 INFO: Trial 1 completed - val_acc: 0.734, val_loss: 0.891",
        "2025-01-15 14:23:12 INFO: Trial 2/50: lr=0.003, batch_size=64, dropout=0.15, epochs=20",
        "2025-01-15 14:23:13 DEBUG: Building CNN model with 3 conv layers",
        "2025-01-15 14:23:14 DEBUG: Starting training... Epoch 1/20",
        "2025-01-15 14:23:15 DEBUG: Epoch 1 - train_loss: 2.101, train_acc: 0.223",
        "2025-01-15 14:23:16 DEBUG: Epoch 2 - train_loss: 1.687, train_acc: 0.398",
        "2025-01-15 14:23:17 DEBUG: Epoch 3 - train_loss: 1.234, train_acc: 0.567",
        "2025-01-15 14:23:18 INFO: Best parameters found: lr=0.003, batch_size=64, dropout=0.15, val_acc=0.892",  # 重要信息1
        "2025-01-15 14:23:19 INFO: Trial 3/50: lr=0.01, batch_size=32, dropout=0.3, epochs=20",
        "2025-01-15 14:23:20 DEBUG: Building CNN model with 3 conv layers",
        "2025-01-15 14:23:21 DEBUG: Starting training... Epoch 1/20",
        "2025-01-15 14:23:22 DEBUG: Epoch 1 - train_loss: 3.456, train_acc: 0.098",
        "2025-01-15 14:23:23 DEBUG: Epoch 2 - train_loss: 4.231, train_acc: 0.087",
        "2025-01-15 14:23:24 ERROR: Gradient explosion detected - lr=0.01 too high, stopping trial",  # 重要信息2
        "2025-01-15 14:23:25 INFO: Trial 4/50: lr=0.0005, batch_size=128, dropout=0.25, epochs=20",
        "2025-01-15 14:23:26 DEBUG: Building CNN model with 3 conv layers",
        "2025-01-15 14:23:27 DEBUG: Starting training... Epoch 1/20",
        "2025-01-15 14:23:28 DEBUG: Epoch 1 - train_loss: 2.087, train_acc: 0.234",
        "2025-01-15 14:23:29 DEBUG: Epoch 5 - train_loss: 0.987, train_acc: 0.678",
        "2025-01-15 14:23:30 DEBUG: Epoch 10 - train_loss: 0.456, train_acc: 0.834",
        "2025-01-15 14:23:31 INFO: New best found: lr=0.0005, batch_size=128, dropout=0.25, val_acc=0.908",  # 重要信息3
        "2025-01-15 14:23:32 DEBUG: Continuing hyperparameter search...",
        "2025-01-15 14:23:33 DEBUG: Evaluating 46 remaining parameter combinations",
        "2025-01-15 14:23:34 INFO: Hyperparameter optimization completed after 50 trials",  # 重要信息4
    ]
    
    # 快速输出所有日志
    for log in logs:
        print(log)
        time.sleep(0.1)  # 快速滚动
    
    print("\n问题：在上面35行调参日志中，你能快速找到4个关键信息吗？")
    print("- 第1次发现好参数（val_acc=0.892）")  
    print("- 1个严重错误（梯度爆炸）")
    print("- 发现最优参数（val_acc=0.908）")
    print("- 调优完成状态")
    print("\n关键问题：哪组参数最优？准确率多少？这些重要信息很难快速找到！")
    print("\n" + "=" * 60 + "\n")

def simulate_rich_notifier_output():
    """使用 Rich Notifier：突出关键的调参发现"""
    print("=" * 60)
    print("Rich Notifier 输出方式 - 机器学习超参数调优")
    print("=" * 60)
    
    # 同样的调参流程，但关键发现用 Notifier 突出
    print("2025-01-15 14:23:01 INFO: Loading dataset: CIFAR-10 (50000 training, 10000 test)")
    print("2025-01-15 14:23:01 DEBUG: Initializing hyperparameter search space")
    print("2025-01-15 14:23:02 INFO: Search space: lr=[0.0001-0.1], batch_size=[16,32,64,128], dropout=[0.1-0.5]")
    print("2025-01-15 14:23:02 DEBUG: Starting hyperparameter optimization with 50 trials")
    print("2025-01-15 14:23:03 INFO: Trial 1/50: lr=0.001, batch_size=32, dropout=0.2, epochs=20")
    print("2025-01-15 14:23:04 DEBUG: Building CNN model with 3 conv layers")
    print("2025-01-15 14:23:05 DEBUG: Model parameters: 2.3M trainable")
    print("2025-01-15 14:23:06 DEBUG: Starting training... Epoch 1/20")
    print("2025-01-15 14:23:07 DEBUG: Epoch 1 - train_loss: 2.234, train_acc: 0.189")
    print("2025-01-15 14:23:08 DEBUG: Epoch 2 - train_loss: 1.987, train_acc: 0.245")
    print("2025-01-15 14:23:09 DEBUG: Epoch 3 - train_loss: 1.756, train_acc: 0.342")
    print("2025-01-15 14:23:10 DEBUG: Early stopping triggered - no improvement for 5 epochs")
    print("2025-01-15 14:23:11 INFO: Trial 1 completed - val_acc: 0.734, val_loss: 0.891")
    print("2025-01-15 14:23:12 INFO: Trial 2/50: lr=0.003, batch_size=64, dropout=0.15, epochs=20")
    print("2025-01-15 14:23:13 DEBUG: Building CNN model with 3 conv layers")
    print("2025-01-15 14:23:14 DEBUG: Starting training... Epoch 1/20")
    print("2025-01-15 14:23:15 DEBUG: Epoch 1 - train_loss: 2.101, train_acc: 0.223")
    print("2025-01-15 14:23:16 DEBUG: Epoch 2 - train_loss: 1.687, train_acc: 0.398")
    print("2025-01-15 14:23:17 DEBUG: Epoch 3 - train_loss: 1.234, train_acc: 0.567")
    
    # 关键发现 - 用 Notifier 突出
    Notifier.success("🎯 发现优秀参数组合 - lr=0.003, dropout=0.15, 验证准确率达到89.2%")
    time.sleep(0.5)
    
    print("2025-01-15 14:23:19 INFO: Trial 3/50: lr=0.01, batch_size=32, dropout=0.3, epochs=20")
    print("2025-01-15 14:23:20 DEBUG: Building CNN model with 3 conv layers")
    print("2025-01-15 14:23:21 DEBUG: Starting training... Epoch 1/20")
    print("2025-01-15 14:23:22 DEBUG: Epoch 1 - train_loss: 3.456, train_acc: 0.098")
    print("2025-01-15 14:23:23 DEBUG: Epoch 2 - train_loss: 4.231, train_acc: 0.087")
    
    # 关键错误 - 用 Notifier 突出
    Notifier.error("❌ 梯度爆炸警告 - 学习率0.01过高，导致训练不稳定")
    time.sleep(0.5)
    
    print("2025-01-15 14:23:25 INFO: Trial 4/50: lr=0.0005, batch_size=128, dropout=0.25, epochs=20")
    print("2025-01-15 14:23:26 DEBUG: Building CNN model with 3 conv layers")
    print("2025-01-15 14:23:27 DEBUG: Starting training... Epoch 1/20")
    print("2025-01-15 14:23:28 DEBUG: Epoch 1 - train_loss: 2.087, train_acc: 0.234")
    print("2025-01-15 14:23:29 DEBUG: Epoch 5 - train_loss: 0.987, train_acc: 0.678")
    print("2025-01-15 14:23:30 DEBUG: Epoch 10 - train_loss: 0.456, train_acc: 0.834")
    
    # 最优发现 - 用 Notifier 突出
    Notifier.success("🏆 找到最优参数 - lr=0.0005, batch_size=128, 验证准确率突破90.8%!")
    time.sleep(0.5)
    
    print("2025-01-15 14:23:32 DEBUG: Continuing hyperparameter search...")
    print("2025-01-15 14:23:33 DEBUG: Evaluating 46 remaining parameter combinations")
    
    # 调优完成状态 - 用面板突出显示
    best_params = {
        "最优学习率": "0.0005",
        "最优批次大小": "128", 
        "最优Dropout率": "0.25",
        "验证准确率": "90.8%",
        "测试准确率": "89.4%",
        "F1分数": "0.891",
        "训练耗时": "45分钟",
        "模型大小": "9.2MB"
    }
    Notifier.show_panel("🏆 超参数调优完成", best_params, border_color="yellow")
    
    print("\n优势：现在你可以一眼看出：")
    print("🟢 2个关键参数发现（绿色突出，一眼看到准确率）")
    print("🔴 1个严重问题（红色警示，避免类似错误）") 
    print("📊 最优参数总结（黄色面板，所有关键指标）")
    print("\n在35行日志中，关键信息瞬间可见！")
    print("\n" + "=" * 60 + "\n")

def demonstrate_code_migration():
    """演示代码迁移的便利性"""
    print("=" * 60)
    print("代码迁移演示：从传统输出到 Rich Notifier")
    print("=" * 60)
    
    print("\n🔧 原始代码（使用 print 和 logger）:")
    print("""
def hyperparameter_search():
    print("开始超参数搜索...")
    
    for trial in range(50):
        params = sample_params()
        print(f"Trial {trial}: {params}")
        
        model = build_model(params)
        score = train_and_evaluate(model)
        
        if score > best_score:
            print(f"New best: {params}, score: {score}")
            best_params = params
            best_score = score
        
        if score < 0.1:  # 训练失败
            print(f"Training failed: {params}")
    
    print(f"Best params: {best_params}, score: {best_score}")
    """)
    
    print("\n🚀 升级后代码（只需替换输出函数）:")
    print("""
from rich_notifier import Notifier

def hyperparameter_search():
    Notifier.info("开始超参数搜索...")
    
    for trial in range(50):
        params = sample_params()
        print(f"Trial {trial}: {params}")  # 普通日志保持不变
        
        model = build_model(params)
        score = train_and_evaluate(model)
        
        if score > best_score:
            # 重要发现用 Notifier 突出！
            Notifier.success(f"🎯 发现更优参数 - 准确率{score:.1%}")
            best_params = params
            best_score = score
        
        if score < 0.1:  # 训练失败
            Notifier.error(f"❌ 训练失败 - {params['lr']}学习率过高")
    
    # 最终结果用面板展示
    Notifier.show_panel("🏆 搜索完成", best_params)
    """)
    
    print("\n📈 实际效果对比:")
    print("\n传统输出:")
    print("Trial 15: lr=0.002, batch_size=64, dropout=0.2")
    print("New best: lr=0.002, batch_size=64, dropout=0.2, score: 0.887")
    print("Trial 28: lr=0.05, batch_size=32, dropout=0.1")
    print("Training failed: lr=0.05, batch_size=32, dropout=0.1")
    
    print("\nRich Notifier 输出:")
    time.sleep(1)
    print("Trial 15: lr=0.002, batch_size=64, dropout=0.2")
    time.sleep(0.5)
    Notifier.success("🎯 发现更优参数 - 准确率88.7%")
    time.sleep(0.5)
    print("Trial 28: lr=0.05, batch_size=32, dropout=0.1")
    time.sleep(0.5)
    Notifier.error("❌ 训练失败 - 0.05学习率过高")
    
    print("\n✨ 升级优势:")
    print("1. 代码结构完全不变")
    print("2. 只需替换输出函数名")
    print("3. 立即获得彩色和格式化效果")
    print("4. 关键信息更加突出")
    print("5. 情绪表达更强烈")

def main():
    """主演示函数"""
    print("🎯 Rich Notifier 核心价值演示")
    print("场景：机器学习超参数调优")
    print("主题：在海量调参日志中，瞬间捕获关键发现")
    print("=" * 60)
    
    input("按 Enter 键开始演示传统输出方式...")
    simulate_traditional_output()
    
    input("按 Enter 键查看 Rich Notifier 输出效果...")
    simulate_rich_notifier_output()
    
    input("按 Enter 键查看代码迁移演示...")
    demonstrate_code_migration()
    
    print("\n🎉 演示完成！")
    print("Rich Notifier 让关键发现在海量日志中一目了然！")
    print("无论是找到最优参数，还是发现训练问题，都能瞬间抓住眼球！")

if __name__ == "__main__":
    main()