from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.v1 import parse as parse_api
from app.api.v1 import vacancies as vacancies_api
from app.api.v1.router import api_router
from app.db.base import Base


@pytest_asyncio.fixture
async def engine(tmp_path: Path):
    db_path = tmp_path / "test.sqlite3"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_maker(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(session_maker):
    async with session_maker() as session:
        yield session


@pytest.fixture
def test_app(session_maker):
    app = FastAPI()
    app.include_router(api_router)

    async def override_get_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[vacancies_api.get_session] = override_get_session
    app.dependency_overrides[parse_api.get_session] = override_get_session
    return app


@pytest_asyncio.fixture
async def api_client(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://testserver",
    ) as client:
        yield client
