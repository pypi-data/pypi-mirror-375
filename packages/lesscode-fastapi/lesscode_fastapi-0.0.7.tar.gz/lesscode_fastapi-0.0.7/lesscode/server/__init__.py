"""
服务启动模块

该模块负责应用程序的初始化和启动，包括：
- 应用实例创建 (app)
- 主入口点 (main)
- 运行脚本 (run)
"""

from .app import create_application
from .run import main

__all__ = [
    "create_application",
    "main"
]