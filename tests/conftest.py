from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture(scope="session")
def client():
    package_dir = Path(__file__).resolve().parents[1] / "src" / "restaurant_reservation"
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False)

    async def get_test_session():
        async with TestSession() as session:
            yield session

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.syspath_prepend(str(package_dir))

        import app as app_module
        from db import get_async_session

        monkeypatch.setattr(app_module, "engine", test_engine)
        monkeypatch.setitem(
            app_module.app.dependency_overrides,
            get_async_session,
            get_test_session,
        )

        with TestClient(app_module.app) as test_client:
            yield test_client


@pytest.fixture(scope="session")
def correct_date() -> str:
    """Возвращает завтрашнюю дату в формате ISO."""
    return (date.today() + timedelta(days=1)).isoformat()


@pytest.fixture
def booking_payload(correct_date):
    """Возвращает заданный и корректный payload для бронирования столика."""
    return {
        "name": "Константин",
        "phone": "+79992558778",
        "booking_date": correct_date,
        "booking_time": "15:00:00",
        "guests": 4,
    }
