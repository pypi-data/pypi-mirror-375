import sys
from pathlib import Path

from loguru import logger

from lesscode.config.settings import Settings


class LoggerSetup:
    """日志配置类"""

    def __init__(self):
        self.settings = Settings()
        self._setup_logger()

    def _setup_logger(self):
        """配置日志系统"""
        # 移除默认的控制台输出
        logger.remove()

        # 确保日志目录存在
        log_file_path = Path(self.settings.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # 添加控制台输出
        logger.add(
            sys.stderr,
            format=self._get_console_format(),
            level=self.settings.log_level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )

        # 添加文件输出
        logger.add(
            self.settings.log_file,
            format=self.settings.log_format,
            level=self.settings.log_level,
            rotation=self.settings.log_rotation,
            retention=self.settings.log_retention,
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=True  # 异步写入
        )

        # 如果是生产环境，添加错误日志文件
        if self.settings.environment == "production":
            error_log_file = self.settings.log_file.replace('.log', '_error.log')
            logger.add(
                error_log_file,
                format=self.settings.log_format,
                level="ERROR",
                rotation=self.settings.log_rotation,
                retention=self.settings.log_retention,
                compression="zip",
                backtrace=True,
                diagnose=True,
                enqueue=True
            )

    def _get_console_format(self):
        """获取控制台日志格式"""
        if self.settings.debug:
            # 开发环境详细格式（行长度可以稍长）
            return ("<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                    "<level>{message}</level>")

        # 生产环境简化格式
        return ("<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<level>{message}</level>")

    def get_logger(self, name: str = None):
        """获取指定名称的日志器"""
        if name:
            return logger.bind(name=name)
        return logger


# 全局日志实例
_LOGGER_SETUP = None


def setup_logging():
    """初始化日志配置"""
    global _LOGGER_SETUP  # pylint: disable=global-statement
    if _LOGGER_SETUP is None:
        _LOGGER_SETUP = LoggerSetup()
    return _LOGGER_SETUP


def get_logger(name: str = None):
    """获取日志器"""
    if _LOGGER_SETUP is None:
        setup_logging()
    return _LOGGER_SETUP.get_logger(name)


# 便捷的日志函数
def log_info(message: str, **kwargs):
    """记录信息日志"""
    get_logger().info(message, **kwargs)


def log_error(message: str, **kwargs):
    """记录错误日志"""
    get_logger().error(message, **kwargs)


def log_warning(message: str, **kwargs):
    """记录警告日志"""
    get_logger().warning(message, **kwargs)


def log_debug(message: str, **kwargs):
    """记录调试日志"""
    get_logger().debug(message, **kwargs)
