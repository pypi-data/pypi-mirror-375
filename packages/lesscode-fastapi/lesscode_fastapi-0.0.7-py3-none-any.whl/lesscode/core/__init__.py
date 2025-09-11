"""
核心组件模块

该模块包含应用程序的核心功能组件，包括：
- 缓存管理 (cache)
- 数据库管理 (database)
- 异常处理 (exception_handlers)
- 异常定义 (exceptions)
- 日志管理 (logging)
- 路由管理 (router)
- 状态码管理 (status_codes)
"""

from .cache import CacheManager, get_cache_manager, cached, cache_clear
from .database import (
    Base,
    engines,
    SessionLocals,
    create_database_engine,
    init_database,
    get_engine,
    get_session_local,
    get_db,
    get_db_context,
    close_all_connections,
    init_all_databases
)
from .exceptions import (
    BaseAppException,
    ValidationException,
    BusinessException,
    ResourceNotFoundException,
    AuthenticationException,
    AuthorizationException,
    DatabaseException,
    CacheException,
    ExternalServiceException
)
from .logging import setup_logging, get_logger, log_info, log_error, log_warning, log_debug
from .router import RouterRegistry, create_router_registry, route_config
from .status_codes import get_business_status

__all__ = [
    "CacheManager",
    "get_cache_manager",
    "cached",
    "cache_clear",
    "Base",
    "engines",
    "SessionLocals",
    "create_database_engine",
    "init_database",
    "get_engine",
    "get_session_local",
    "get_db",
    "get_db_context",
    "close_all_connections",
    "init_all_databases",
    "BaseAppException",
    "ValidationException",
    "BusinessException",
    "ResourceNotFoundException",
    "AuthenticationException",
    "AuthorizationException",
    "DatabaseException",
    "CacheException",
    "ExternalServiceException",
    "setup_logging",
    "get_logger",
    "log_info",
    "log_error",
    "log_warning",
    "log_debug",
    "RouterRegistry",
    "create_router_registry",
    "route_config",
    "get_business_status"
]