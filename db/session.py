from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from core.settings import settings, DatabaseSettings
from core.logger import get_logger

logger = get_logger(__name__)


_engine: Optional[AsyncEngine] = None
_session_local: Optional[async_sessionmaker[AsyncSession]] = None


def is_database_configured(db_settings: Optional[DatabaseSettings] = None) -> bool:
    db = db_settings or settings.database
    if not db.get_dsn():
        return False
    return True


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        dsn = settings.database.get_dsn()
        if not dsn:
            raise ValueError("数据库配置不完整，请检查环境变量")
        _engine = create_async_engine(
            dsn,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_recycle=settings.database.pool_recycle,
            echo=settings.database.echo,
        )
    return _engine


def get_session_local() -> async_sessionmaker[AsyncSession]:
    global _session_local
    if _session_local is None:
        engine = get_engine()
        _session_local = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_local


AsyncSessionLocal = get_session_local


async def create_tables() -> None:
    from db.base import Base

    if not is_database_configured():
        logger.warning("数据库未配置，跳过表创建")
        return

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表创建完成")


async def close_db_pool() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        logger.info("数据库连接池已关闭")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    if not is_database_configured():
        logger.warning("数据库未配置，无法获取会话")
        raise RuntimeError("数据库未配置")

    session_local = get_session_local()
    async with session_local() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
