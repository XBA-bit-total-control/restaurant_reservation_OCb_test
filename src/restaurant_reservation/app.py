from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import engine
from models import Base
from routes import router


# Думал сначала применять Alembic, но после решил что избыточно
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создаёт таблицы при запуске, освобождает соединения при остановке."""
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="Table booker",
    description="REST API for table reservation",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, tags=["bookings"])


@app.get("/")
async def root():
    """Возвращает сообщение о работе API."""
    return {"message": "Table booker API is running"}
