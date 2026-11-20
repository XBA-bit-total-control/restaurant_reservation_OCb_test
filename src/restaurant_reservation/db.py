from pathlib import Path
from typing import Any, AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


project_root = Path(__file__).resolve().parents[2]
db_path = project_root / "bookings.db"
db_url = URL.create("sqlite+aiosqlite", database=str(db_path))

engine = create_async_engine(db_url)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[Any, None]:
    """Открывает сессию базы данных на время запроса."""
    async with Session() as session:
        yield session
