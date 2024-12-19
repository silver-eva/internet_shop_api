from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.lib.config import config

url = f"postgresql+asyncpg://{config.db_user}:{config.db_pass}@{config.db_host}:{config.db_port}/{config.db_name}"
engine = create_async_engine(
    url,
    echo=True,
    future=True,
    pool_pre_ping=True
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
