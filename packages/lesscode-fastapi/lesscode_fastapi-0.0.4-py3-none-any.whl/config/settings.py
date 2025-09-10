"""
应用程序配置设置模块

该模块使用Pydantic Settings为FastAPI应用程序定义配置设置。

设置从环境变量和YAML配置文件加载，并提供合理的默认值。

主要功能：
- Settings: 基础配置类，包含所有应用配置项
- load_config_from_file: 从YAML文件加载配置
- get_settings: 获取配置实例的静态方法（带LRU缓存）

配置项包括：
- 应用基础配置（名称、版本、调试模式等）
- 服务器配置（监听地址、端口等）
- 数据库配置（连接URL、连接池等）
- Redis配置（连接URL、启用状态等）
- 日志配置（级别、文件路径、格式等）
- JWT配置（密钥、算法、过期时间等）
- CORS配置（允许的源、方法、请求头等）
- 分页配置（默认页面大小、最大页面大小等）
- 缓存配置（启用状态、TTL、键前缀等）
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict, Union

import yaml
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用基础配置类，继承自 BaseSettings，用于管理应用的各种配置项。
    支持从环境变量中读取配置，并可区分不同运行环境（开发、生产、测试）。
    """

    # 应用基础配置
    app_name: str = "FastAPI Scaffold"  # 应用名称
    app_version: str = "1.0.0"  # 应用版本号
    debug: bool = False  # 是否开启调试模式
    environment: str = "dev"  # 当前运行环境标识

    # 服务器配置
    host: str = "0.0.0.0"  # 服务监听地址
    port: int = 8000  # 服务监听端口
    reload: bool = False  # 是否开启热重载（开发时使用）

    # 数据库配置
    database_url: Optional[str] = None  # 主数据库连接URL
    database_pool_size: int = 10  # 数据库连接池大小
    database_max_overflow: int = 20  # 数据库连接池最大溢出数

    # 多数据源配置
    database_urls: Dict[str, str] = {}  # 多个数据库连接配置，键为标识符，值为连接URL

    # Redis配置
    redis_url: Optional[str] = None  # Redis连接URL
    redis_enabled: bool = False  # 是否启用Redis功能

    # 日志配置
    log_level: str = "INFO"  # 日志级别
    log_file: str = "logs/app.log"  # 日志文件路径
    log_rotation: str = "10 MB"  # 日志轮转大小
    log_retention: str = "10 days"  # 日志保留时间
    log_format: str = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    )
    # 日志输出格式

    # JWT配置
    secret_key: str = "your-secret-key-here"  # JWT签名密钥
    algorithm: str = "HS256"  # JWT加密算法
    access_token_expire_minutes: int = 30  # 访问令牌过期时间（分钟）

    # CORS配置
    allowed_origins: list = ["*"]  # 允许跨域请求的源列表
    allowed_methods: list = ["*"]  # 允许的HTTP方法
    allowed_headers: list = ["*"]  # 允许的请求头字段

    # 分页配置
    default_page_size: int = 20  # 默认分页大小
    max_page_size: int = 100  # 最大分页大小限制

    # 缓存配置
    cache_enabled: bool = False  # 全局缓存开关
    cache_default_ttl: int = 300  # 默认缓存时间（秒）
    cache_refresh_threshold: int = 60  # 缓存刷新阈值（秒）
    cache_key_prefix: str = "app"  # 缓存键前缀

    model_config = ConfigDict(
        extra='allow'  # 允许额外字段
    )

    @classmethod
    @field_validator('database_urls', mode='before')
    def parse_database_urls(cls, v):
        """
        解析字符串格式的多数据源配置。
        输入格式应为："db1=url1,db2=url2"

        Args:
            v: 待解析的原始输入值，可以是字符串或字典

        Returns:
            Dict[str, str]: 转换后的数据库连接配置字典
        """
        if isinstance(v, str):
            if v:
                return dict(item.split('=') for item in v.split(',') if '=' in item)
        return v or {}

    @staticmethod
    def load_config_from_file(config_path: Union[str, Path]) -> "Settings":
        """
        从配置文件加载配置信息
        支持的文件格式：
        - .yaml/.yml: YAML格式

        Args:
            config_path: 配置文件路径

        Returns:
            Settings: 加载了配置信息的 Settings 实例

        Raises:
            FileNotFoundError: 当指定的配置文件不存在时抛出异常
        """
        config_path = Path(config_path)
        settings = Settings()

        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        # 加载配置文件
        config_data = {}
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f) or {}
        if config_data:
            for key, value in config_data.items():
                setattr(settings, key, value)
        return settings

    @staticmethod
    @lru_cache(maxsize=1)
    def get_settings() -> "Settings":
        """
        获取配置实例（单例模式），使用 LRU 缓存确保仅在首次调用时创建一次。

        Returns:
            Settings: 配置类的实例。
        """
        print("Creating new Settings instance")  # 或使用打印语句
        env = os.getenv("LESS_CODE_ENVIRONMENT", "dev")
        env_file = f"config/{env}.yaml"
        if env_file and Path(env_file).exists():
            settings = Settings.load_config_from_file(env_file)
        else:
            settings = Settings()
        return settings
