from contextlib import contextmanager
from typing import Optional, Dict, Any

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from lesscode.config.settings import Settings
from lesscode.core.logging import get_logger

logger = get_logger(__name__)
settings = Settings()

# 数据库基础类
Base = declarative_base()

# 数据库引擎字典（支持多数据源）
engines: Dict[str, Any] = {}
SessionLocals: Dict[str, Any] = {}


def create_database_engine(database_url: str, **kwargs):
    """创建数据库引擎"""
    engine_kwargs = {
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
        "pool_pre_ping": True,
        "pool_recycle": 3600,  # 1小时后回收连接
        **kwargs
    }

    # SQLite不支持连接池参数
    if database_url.startswith("sqlite"):
        engine_kwargs = {"pool_pre_ping": True}

    return create_engine(database_url, **engine_kwargs)


def init_database(database_name: str = "default", database_url: Optional[str] = None):
    """初始化数据库连接"""
    if database_url is None:
        if database_name == "default":
            database_url = settings.database_url
        else:
            database_url = settings.database_urls.get(database_name)
            if not database_url:
                raise ValueError(f"Database URL not found for: {database_name}")

    if database_name in engines:
        logger.info(f"Database engine already exists for: {database_name}")
        return

    try:
        engine = create_database_engine(database_url)
        engines[database_name] = engine
        SessionLocals[database_name] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info(f"Database initialized successfully: {database_name}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"Failed to initialize database {database_name}: {str(e)}")
        raise


def get_engine(database_name: str = "default"):
    """获取数据库引擎"""
    if database_name not in engines:
        init_database(database_name)
    return engines[database_name]


def get_session_local(database_name: str = "default"):
    """获取SessionLocal类"""
    if database_name not in SessionLocals:
        init_database(database_name)
    return SessionLocals[database_name]


def get_db(database_name: str = "default") -> Session:
    """获取数据库会话（依赖注入用）"""
    session_local = get_session_local(database_name)
    db = session_local()
    try:
        yield db
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context(database_name: str = "default"):
    """获取数据库会话上下文管理器"""
    session_local = get_session_local(database_name)
    db = session_local()
    try:
        yield db
        db.commit()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.error(f"Database context error: {str(exc)}")
        db.rollback()
        raise
    finally:
        db.close()


# def create_tables(database_name: str = "default"):
#     """创建数据库表"""
#     engine = get_engine(database_name)
#     Base.metadata.create_all(bind=engine)
#     logger.info(f"Database tables created for: {database_name}")
#
#
# def drop_tables(database_name: str = "default"):
#     """删除数据库表"""
#     engine = get_engine(database_name)
#     Base.metadata.drop_all(bind=engine)
#     logger.info(f"Database tables dropped for: {database_name}")


def close_all_connections():
    """关闭所有数据库连接"""
    for database_name, engine in engines.items():
        try:
            engine.dispose()
            logger.info(f"Database connection closed: {database_name}")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Error closing database connection {database_name}: {str(e)}")

    engines.clear()
    SessionLocals.clear()


# 数据库初始化（在应用启动时调用）
def init_all_databases():
    """初始化所有配置的数据库"""
    try:
        # 初始化默认数据库
        if settings.database_url:
            init_database("default", settings.database_url)

        # 初始化多数据源
        for db_name, db_url in settings.database_urls.items():
            if db_name != "default":  # 避免重复初始化默认数据库
                init_database(db_name, db_url)

        logger.info("All databases initialized successfully")
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"Failed to initialize databases: {str(e)}")
        raise
