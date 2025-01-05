from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import Executable

from typing import Literal, Iterable

from lib.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session

async def db_execute(
        db: AsyncSession, 
        statement: Executable, 
        with_result: Literal["all", "one", "raw_all", "raw_one"] = None) -> Iterable[Base] | Base | None:
    results_map = {
        "all": lambda x: x.scalars().all(),
        "one": lambda x: x.scalar(),
        "raw_all": lambda x: x.fetchall(),
        "raw_one": lambda x: x.fetchone()
    }
    try:
        result = await db.execute(statement)
        await db.commit()
    except Exception as e:
        raise e
    
    return results_map.get(with_result, lambda x: None)(result)