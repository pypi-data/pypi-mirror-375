"""
可重用的终端通知模块
基于 rich 库，提供标准化的信息、成功、警告、错误和面板输出。
"""

from rich import print
from rich.panel import Panel

class Notifier:
    """
    一个提供静态方法的通知器类，用于在终端输出格式化的信息。
    """

    @staticmethod
    def info(message: str):
        """打印普通的信息性文本。"""
        print(message)

    @staticmethod
    def success(message: str):
        """打印高亮的成功信息 (亮青背景，黑色文字)。"""
        print(f"[black on color(45)]{message}[/black on color(45)]")

    @staticmethod
    def warning(message: str):
        """打印警告或中间状态信息 (黄色下划线)。"""
        print(f"[underline yellow]{message}[/underline yellow]")

    @staticmethod
    def error(message: str):
        """打印醒目的错误信息 (红色，加粗)。"""
        print(f"[bold red]{message}[/bold red]")

    @staticmethod
    def show_panel(title: str, content: dict, border_color: str = "green"):
        """
        显示一个带有标题和彩色边框的面板，用于突出展示结构化的重要信息。

        Args:
            title (str): 面板顶部显示的标题。
            content (dict): 一个字典，其键值对将被格式化后显示在面板内部。
            border_color (str): 面板边框的颜色，默认为 'green'。
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