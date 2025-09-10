"""Tests a mock Starlette worker."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from typing_extensions import TypedDict

from asgi_sqlalchemy.context import DatabaseContext
from asgi_sqlalchemy.middleware import SessionMiddleware
from asgi_sqlalchemy.starlette import get_session


async def hello_world(request: Request) -> JSONResponse:
    """Return a greeting after touching the request/session."""
    # Touch request so it isn't unused
    _ = request.scope.get("type")
    return JSONResponse({"hello": "world!"})


@pytest_asyncio.fixture
async def starlette_app(database: DatabaseContext) -> AsyncGenerator[Starlette]:
    """Starlette fixture with database lifespan."""

    class AppState(TypedDict):
        db: DatabaseContext

    @asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncGenerator[AppState]:  # noqa: ARG001
        yield {"db": database}

    app = Starlette(routes=[Route("/handle", hello_world)], lifespan=lifespan)
    app.add_middleware(SessionMiddleware)  # type: ignore  # noqa: PGH003
    yield app


@pytest_asyncio.fixture
async def client(starlette_app: Starlette) -> AsyncGenerator[AsyncClient]:
    """Create a test async client with lifespan support."""
    async with (
        LifespanManager(starlette_app) as manager,
        AsyncClient(
            transport=ASGITransport(manager.app),
            base_url="http://test",
            follow_redirects=True,
        ) as client,
    ):
        yield client


async def test_successful_handler(client: AsyncClient) -> None:
    """Tests that we can call a handler with no dependency and it works."""
    response = await client.get("/handle")
    assert response.status_code == 200
    assert response.json() == {"hello": "world!"}


async def test_database_unhandled_rollback(
    starlette_app: Starlette, client: AsyncClient, database: DatabaseContext
) -> None:
    """Tests that an unhandled exception in our database rolls back."""
    async with database.session_maker() as session:
        await session.execute(
            text(
                """CREATE TABLE IF NOT EXISTS temp_test_table1 (
                value INTEGER
            )"""
            )
        )
        await session.commit()

    error = "I am an unhandled exception!"

    async def trigger_error(request: Request) -> JSONResponse:
        session = await get_session(request)
        await session.execute(
            text("INSERT INTO temp_test_table1 (value) VALUES (2001)")
        )
        raise ValueError(error)

    starlette_app.router.routes.append(
        Route("/error1", trigger_error, methods=["POST"])
    )

    with pytest.raises(ValueError, match=error):
        await client.post("/error1")

    async with database.session_maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM temp_test_table1"))
        count = result.scalar()
        assert count == 0


async def test_database_doesnt_rollback(
    starlette_app: Starlette, client: AsyncClient, database: DatabaseContext
) -> None:
    """Tests that a handled exception in our database rolls back."""
    async with database.session_maker() as session:
        await session.execute(
            text(
                """CREATE TABLE IF NOT EXISTS temp_test_table2 (
                value INTEGER
            )"""
            )
        )
        await session.commit()

    error = "I am a handled exception!"

    async def trigger_error(request: Request) -> JSONResponse:
        session = await get_session(request)
        await session.execute(
            text("INSERT INTO temp_test_table2 (value) VALUES (2001)")
        )
        return JSONResponse({"detail": error}, status_code=303)

    starlette_app.router.routes.append(
        Route("/error2", trigger_error, methods=["POST"])
    )

    response = await client.post("/error2")
    assert response.status_code == 303
    assert response.json() == {"detail": error}

    async with database.session_maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM temp_test_table2"))
        count = result.scalar()
        assert count == 1


async def test_database_manual_rollback(
    starlette_app: Starlette, client: AsyncClient, database: DatabaseContext
) -> None:
    """Tests that a handled exception with a manual rollback rolls back."""
    async with database.session_maker() as session:
        await session.execute(
            text(
                """CREATE TABLE IF NOT EXISTS temp_test_table3 (
                value INTEGER
            )"""
            )
        )
        await session.commit()

    error = "I am a handled exception!"

    async def trigger_error(request: Request) -> JSONResponse:
        session = await get_session(request)
        await session.execute(
            text("INSERT INTO temp_test_table3 (value) VALUES (2001)")
        )
        await session.rollback()
        return JSONResponse({"detail": error}, status_code=303)

    starlette_app.router.routes.append(
        Route("/error3", trigger_error, methods=["POST"])
    )

    response = await client.post("/error3")
    assert response.status_code == 303
    assert response.json() == {"detail": error}

    async with database.session_maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM temp_test_table3"))
        count = result.scalar()
        assert count == 0
