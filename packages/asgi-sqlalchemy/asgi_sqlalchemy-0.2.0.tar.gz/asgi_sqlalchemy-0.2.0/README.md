# asgi-sqlalchemy

ASGI Middleware that manages the lifespan of a database engine and a corresponding session, featuring no global state, and automatic rollbacks on unhandled exceptions. Includes FastAPI and Starlette integrations.

I wrote about my motivations for this library in-depth [here](https://abhi.rodeo/posts/programming/languages/python/fastapi/globals-in-fastapi/), but the short version is that using the ASGI lifespan protocol, we can avoid the use of global state, making database access more predictable and easier to test/mock.

## Installation:

```bash
uv add asgi-sqlalchemy
```

## Usage:

### FastAPI:

```python
from contextlib import AsyncContextManager
from collections.abc import AsyncGenerator
from typing_extensions import TypedDict

from fastapi import FastAPI

from asgi_sqlalchemy import DatabaseContext, SessionMiddleware
from asgi_sqlalchemy.fastapi import SessionDependency

class AppState(TypedDict):
    db: DatabaseContext

async def lifespan() -> AsyncGenerator[AppState]:
    async with DatabaseContext(...) as db:
        yield {"db": db}

app = FastAPI()
app.add_middleware(SessionMiddleware)

@app.get("/db")
async def handler(session: SessionDependency) -> str:
    # do something with your async session!
```

### Starlette:

```python
from contextlib import AsyncContextManager
from collections.abc import AsyncGenerator
from typing_extensions import TypedDict

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from asgi_sqlalchemy import DatabaseContext, SessionMiddleware
from asgi_sqlalchemy.starlette import get_session

class AppState(TypedDict):
    db: DatabaseContext

async def lifespan() -> AsyncGenerator[AppState]:
    async with DatabaseContext(...) as db:
        yield {"db": db}

async def handler(request: Request) -> JSONResponse:
    session = await get_session(request)
    # do something with your async session!

app = Starlette(routes=[Route("/db", handler)], lifespan=lifespan)
app.add_middleware(SessionMiddleware)
```

### Tests:

This library was explicitly designed to be easy to test without dependency overrides.

- For synchronous tests, use FastAPI's `TestClient`.
- For asynchronous tests, use HTTPX `AsyncClient` with `ASGITransport`, and wrap the app with `LifespanManager` so startup/shutdown events run. See the FastAPI docs: [Async Tests – In Detail](https://fastapi.tiangolo.com/advanced/async-tests/?h=lifespanmanager#in-detail).
- To “mock” your database, provide a custom lifespan in tests that yields the database object you want (real DB or test double). The middleware will inject a fresh session per request, no dependency overrides needed.

See complete examples in [`tests/test_fastapi.py`](./tests/test_fastapi.py) and [`tests/test_starlette.py`](./tests/test_starlette.py) inside the [`tests/`](./tests/) folder.