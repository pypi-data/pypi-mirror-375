"""
配置管理模块

该模块负责管理应用程序的各种配置设置，包括：
- 应用基础配置
- 数据库配置
- Redis配置
- 日志配置
- JWT配置
- CORS配置
- 分页配置
- 缓存配置
"""

from .settings import Settings

__all__ = [
    "Settings"
]