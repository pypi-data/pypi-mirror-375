"""
PowerShell 兼容的终端通知模块
针对 PowerShell 加粗颜色显示问题的优化版本
"""

from rich import print
from rich.panel import Panel

class PSNotifier:
    """
    PowerShell 兼容的通知器类
    解决加粗颜色在 PowerShell 中显示异常的问题
    """

    @staticmethod
    def info(message: str):
        """打印普通的信息性文本。"""
        print(message)

    @staticmethod
    def success(message: str):
        """打印成功信息 (亮绿色 + 符号)。"""
        print(f"[bright_green]✓ {message}[/bright_green]")

    @staticmethod
    def warning(message: str):
        """打印警告信息 (亮黄色 + 符号)。"""
        print(f"[bright_yellow]⚠ {message}[/bright_yellow]")

    @staticmethod
    def error(message: str):
        """打印错误信息 (亮红色 + 符号)。"""
        print(f"[bright_red]✗ {message}[/bright_red]")

    @staticmethod
    def show_panel(title: str, content: dict, border_color: str = "green"):
        """
        显示一个带有标题和彩色边框的面板。
        """
        panel_content = ""
        for key, value in content.items():
            panel_content += f"[bold]{key}:[/] {value}\n"
        
        panel = Panel(
            panel_content.strip(),
            title=title,
            border_style=border_color,
            expand=True
        )
        print(panel)


# 别名，方便替换使用
Notifier = PSNotifier