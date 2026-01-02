from collections.abc import AsyncGenerator

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from ..configs import db_conf

engine = create_async_engine(db_conf.conn_url())
async_session_factory = async_sessionmaker(engine, expire_on_commit=True, autoflush=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        except exc.SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()
