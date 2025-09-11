import asyncio
import hashlib
import json
import time
from functools import wraps
from typing import Any, Optional, Dict, Union, Callable

import redis.asyncio as redis

from lesscode.config.settings import Settings
from lesscode.core.logging import get_logger

logger = get_logger(__name__)


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self.settings = Settings.get_settings()
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = self.settings.cache_enabled and self.settings.redis_enabled
        self._background_tasks: Dict[str, asyncio.Task] = {}

        if self.enabled and self.settings.redis_url:
            asyncio.create_task(self._init_redis())

    async def _init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True  # 支持JSON序列化
            )
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Failed to initialize Redis: {str(e)}")
            self.enabled = False

    async def get_with_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """获取缓存值及其元数据"""
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                cache_data = json.loads(value)
                return cache_data
            return None
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        cache_data = await self.get_with_metadata(key)
        if cache_data:
            return cache_data.get("value")
        return None

    async def set(
            self,
            key: str,
            value: Any,
            expire: int = None,
    ) -> bool:
        """设置缓存值"""
        if not self.enabled or not self.redis_client:
            return False

        if expire is None:
            expire = self.settings.cache_default_ttl

        try:
            # 存储带时间戳的缓存数据
            cache_data = {
                "value": value,
                "timestamp": time.time(),
                "ttl": expire
            }

            serialized_value = json.dumps(cache_data, default=str)
            await self.redis_client.set(key, serialized_value, ex=expire)
            return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Cache exists error for key {key}: {str(e)}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            return await self.redis_client.expire(key, seconds)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Cache expire error for key {key}: {str(e)}")
            return False

    def should_refresh_cache(self, cache_data: dict) -> bool:
        """判断是否需要后台刷新缓存"""
        timestamp = cache_data.get("timestamp", 0)
        current_time = time.time()
        cache_age = current_time - timestamp

        return cache_age >= self.settings.cache_refresh_threshold

    async def refresh_cache_background(self, key: str, func: Callable, args: tuple, kwargs: dict,
                                       ttl: int):
        """后台刷新缓存"""
        try:
            # 避免重复的后台任务
            if key in self._background_tasks and not self._background_tasks[key].done():
                return

            logger.info(f"Starting background cache refresh for key: {key}")

            # 执行原函数获取新数据
            if asyncio.iscoroutinefunction(func):
                new_value = await func(*args, **kwargs)
            else:
                new_value = func(*args, **kwargs)

            # 更新缓存
            await self.set(key, new_value, ttl)
            logger.info(f"Background cache refresh completed for key: {key}")

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Background cache refresh failed for key {key}: {e}")
        finally:
            # 清理任务引用
            if key in self._background_tasks:
                del self._background_tasks[key]

    def _generate_cache_key(self, prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        # 创建参数的唯一标识
        params_str = json.dumps({
            "args": [str(arg) for arg in args],
            "kwargs": {k: str(v) for k, v in kwargs.items()}
        }, sort_keys=True)

        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{self.settings.cache_key_prefix}:{prefix}:{func_name}:{params_hash}"

    async def clear_pattern(self, pattern: str) -> int:
        """根据模式删除缓存"""
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Cache clear pattern error for pattern {pattern}: {str(e)}")
            return 0

    async def close(self):
        """关闭连接"""
        if self.redis_client:
            await self.redis_client.close()


# 全局缓存实例
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# 缓存装饰器
def cached(
        key_prefix: str = "default",
        expire: int = None,
        enabled: Optional[bool] = None,
        refresh_threshold: Optional[int] = None
):
    """
    缓存装饰器 - 支持系统级配置和后台刷新

    Args:
        key_prefix: 缓存键前缀
        expire: 缓存存活时间(秒)，None使用系统默认值
        enabled: 是否启用缓存，None使用系统配置
        refresh_threshold: 刷新阈值(秒)，None使用系统配置
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = get_cache_manager()

            # 检查缓存是否启用
            cache_enabled = enabled if enabled is not None else cache.settings.cache_enabled
            if not cache_enabled or not cache.enabled:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            # 生成缓存键
            cache_key = cache._generate_cache_key(key_prefix, func.__name__, args, kwargs)

            # 尝试获取缓存及元数据
            cache_data = await cache.get_with_metadata(cache_key)

            cache_ttl = expire or cache.settings.cache_default_ttl

            if cache_data:
                # 检查是否需要后台刷新
                if cache.should_refresh_cache(cache_data):
                    # 启动后台刷新任务
                    task = asyncio.create_task(
                        cache.refresh_cache_background(
                            cache_key, func, args, kwargs, cache_ttl
                        )
                    )
                    cache._background_tasks[cache_key] = task

                logger.debug(f"Cache hit for key: {cache_key}")
                return cache_data["value"]

            # 缓存未命中，执行原函数
            logger.debug(f"Cache miss for key: {cache_key}")

            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # 设置缓存
            await cache.set(cache_key, result, cache_ttl)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 对于同步函数，需要在异步上下文中运行
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            return loop.run_until_complete(async_wrapper(*args, **kwargs))

        # 根据函数类型返回对应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# 缓存清除装饰器
def cache_clear(key_patterns: Union[str, list]):
    """缓存清除装饰器"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            cache = get_cache_manager()
            if cache.enabled:
                patterns = [key_patterns] if isinstance(key_patterns, str) else key_patterns
                for pattern in patterns:
                    await cache.clear_pattern(pattern)
                    logger.debug(f"Cache cleared for pattern: {pattern}")

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            return loop.run_until_complete(async_wrapper(*args, **kwargs))

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
