"""Starlette-specific helper utilities."""

from __future__ import annotations

from importlib.util import find_spec
from typing import TYPE_CHECKING

if find_spec("starlette") is not None:
    from starlette.requests import Request  # noqa: TC002
else:  # pragma: no cover
    msg = "Starlette not found, please install asgi-sqlalchemy[starlette]"
    raise ImportError(msg)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ("get_session",)


async def get_session(request: Request) -> AsyncSession:
    """Get the `AsyncSession` put in the scope of the request via Middleware."""
    return request.scope.get("db_session")  # type: ignore  # noqa: PGH003
