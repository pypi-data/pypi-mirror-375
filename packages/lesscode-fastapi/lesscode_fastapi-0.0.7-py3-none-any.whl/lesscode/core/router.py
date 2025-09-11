import importlib
import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, APIRouter

from lesscode.core.logging import get_logger

logger = get_logger(__name__)


class RouterRegistry:
    """路由注册器"""

    def __init__(self, app: FastAPI):
        self.app = app
        self.routers: List[APIRouter] = []

    def register_router(self, router: APIRouter, prefix: str = "", tags: List[str] = None):
        """注册单个路由"""
        self.app.include_router(router, prefix=prefix, tags=tags or [])
        self.routers.append(router)
        logger.info(f"Router registered: {prefix}")

    def auto_register_routers(self, router_directory: str = "handlers"):
        """自动注册路由目录下的所有路由"""
        router_path = Path(router_directory)

        if not router_path.exists():
            logger.warning(f"Router directory not found: {router_directory}")
            return

        # 递归扫描所有Python文件
        for router_file in router_path.rglob("*.py"):
            if router_file.name.startswith("__"):
                continue

            try:
                # 构建模块路径 (handlers.user.main -> handlers.user.main)
                module_name = str(router_file.with_suffix('')).replace(os.sep, ".")

                # 动态导入模块
                module = importlib.import_module(module_name)

                # 遍历模块中所有属性，查找APIRouter对象
                for attr_name in dir(module):
                    attr_value = getattr(module, attr_name)
                    if isinstance(attr_value, APIRouter):
                        # 从APIRouter对象本身获取前缀和标签
                        prefix = getattr(attr_value, 'prefix', None) or f"/{router_file.stem}"
                        tags = getattr(attr_value, 'tags', None) or [
                            router_file.stem.replace('_', ' ').title()]

                        # 如果前缀不是以/开头，添加/
                        if prefix and not prefix.startswith("/"):
                            prefix = f"/{prefix}"

                        self.register_router(attr_value, prefix=prefix, tags=tags)
                        logger.info(f"Found APIRouter: {attr_name} in {module_name}")

            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(f"Failed to load router from {router_file}: {str(e)}")

    def get_registered_routers(self) -> List[APIRouter]:
        """获取已注册的路由列表"""
        return self.routers


def create_router_registry(app: FastAPI) -> RouterRegistry:
    """创建路由注册器实例"""
    return RouterRegistry(app)


# 装饰器用于标记路由模块
def route_config(prefix: str = None, tags: List[str] = None):
    """路由配置装饰器"""

    def decorator(cls):
        if prefix:
            cls.PREFIX = prefix
        if tags:
            cls.TAGS = tags
        return cls

    return decorator
