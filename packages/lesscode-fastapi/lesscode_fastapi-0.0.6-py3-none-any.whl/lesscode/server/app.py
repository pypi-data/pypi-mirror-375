from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lesscode.config.settings import Settings
from lesscode.core.cache import get_cache_manager
from lesscode.core.database import init_all_databases, close_all_connections
from lesscode.core.exception_handlers import register_exception_handlers
from lesscode.core.router import create_router_registry
from lesscode.utils.response import success_response

settings = Settings.get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    # setup_logging()
    init_all_databases()

    # 初始化缓存
    cache_manager = get_cache_manager()

    yield

    # 关闭时执行
    await cache_manager.close()
    close_all_connections()


def create_application() -> FastAPI:
    """创建FastAPI应用实例"""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/swagger" if settings.environment != "pro" else None,
        lifespan=lifespan
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )

    # 注册异常处理器
    register_exception_handlers(app)

    # 自动注册路由
    router_registry = create_router_registry(app)
    router_registry.auto_register_routers()

    # 健康检查端点
    @app.get("/health", tags=["健康检查"])
    async def health_check():
        return success_response(
            data={
                "app_name": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment
            },
            message="系统运行正常"
        )

    return app
