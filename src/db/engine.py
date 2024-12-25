from typing import Iterable, Literal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from sqlalchemy.sql import Executable

from src.lib.config import config
from src.db.models import BaseModel

url = f"postgresql+asyncpg://{config.db_user}:{config.db_pass}@{config.db_host}:{config.db_port}/{config.db_name}"
engine = create_async_engine(
    url,
    echo=True,
    future=True,
    pool_pre_ping=True
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session():
    async with async_session() as session:
        yield session


async def db_execute(
        db: AsyncSession, 
        query: Executable,
        with_result: Literal["all", "one"] = "",
        ) -> Iterable[BaseModel] | BaseModel | None:
    results_map = {
        "all": lambda x: x.scalars().all(),
        "one": lambda x: x.scalar(),
        "raw_all": lambda x: x.fetchall(),
        "raw_one": lambda x: x.fetchone(),
        "": lambda x: None
    }
    try:
        result = await db.execute(query)
        await db.commit()
    except Exception as e:
        raise e
    
    return results_map.get(with_result, lambda x: x)(result)