#!/usr/bin/env python3
import argparse
import os

import uvicorn

from lesscode.config.settings import Settings
from lesscode.server import create_application


def main():
    """主启动函数"""
    parser = argparse.ArgumentParser(description="LessCode-FastAPI 启动脚本")
    parser.add_argument("--env", default="dev",
                        choices=["dev", "pro", "test"],
                        help="运行环境")
    parser.add_argument("--config", type=str, default=None,
                        help="配置文件路径 (支持 .env, .json, .yaml 格式)")
    parser.add_argument("--host", default=None, help="绑定主机地址")
    parser.add_argument("--port", type=int, default=None, help="端口号")
    parser.add_argument("--reload", action="store_true", help="启用热重载")
    parser.add_argument("--workers", type=int, default=1, help="工作进程数")

    args = parser.parse_args()

    # 设置环境变量
    os.environ["LESS_CODE_ENVIRONMENT"] = args.env
    # 加载环境配置文件
    settings = Settings.get_settings()

    # 设置运行参数
    host = args.host or settings.host
    port = args.port or settings.port
    reload = args.reload or settings.reload

    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Host: {host}:{port}")
    print(f"Debug mode: {settings.debug}")
    print(f"Reload: {reload}")
    # 创建应用实例
    app = create_application()
    # 启动服务
    if args.env == "pro":
        # 生产环境使用多进程
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=args.workers,
            log_level=settings.log_level.lower()
        )
    else:
        # 开发/测试环境
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level=settings.log_level.lower()
        )


if __name__ == "__main__":
    main()
