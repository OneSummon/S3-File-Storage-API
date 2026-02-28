import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from dotenv import load_dotenv

load_dotenv()

engine = create_async_engine(url=os.getenv("DB_URL"), echo=True)

async_session = async_sessionmaker(engine)


async def get_session() -> AsyncSession: # type: ignore
    async with async_session() as session:
        yield session