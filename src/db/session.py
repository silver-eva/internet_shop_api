from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Executable

from typing import Iterable, Literal

from src.db.connect import async_session
from src.db.models import BaseModel

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
        "one": lambda x: x.scalars().one()
    }
    try:
        result = await db.execute(query)
        await db.commit()
    except Exception as e:
        raise e
    
    return results_map.get(with_result, lambda x: x)(result)
