# from curses import echo

from sqlmodel import SQLModel
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from test.test_wsgiref import WSGIRequestHandler
from src.config import config
from sqlalchemy.ext.asyncio import create_async_engine

# engine=create_async_engine(url=config.DATABASE_URL,echo=True)
# engine=create_async_engine(url=config.DATABASE_URL)
engine = create_async_engine(
    url=config.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)
from src.auth.model import User  #! the model should be imported before the metadata


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session
