from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from dishka.async_container import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.core.config import settings
from src.infrastructure.di import ApplicationContainer
from src.infrastructure.postgres.mappings.all import map_tables
from src.presentation.api.exception_handlers import register_exception_handlers
from src.presentation.api.routes import router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    yield


def include_routes(app: FastAPI) -> None:
    app.include_router(router)


def create_app() -> FastAPI:
    app = FastAPI(
        version=settings.application.version,
        title=settings.application.title,
        description=settings.application.description,
        debug=settings.application.debug,
        lifespan=lifespan,
    )
    map_tables()
    container = make_async_container(ApplicationContainer())
    setup_dishka(container, app)
    include_routes(app)
    register_exception_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("src.presentation.api.main:app", host="0.0.0.0", port=8000, reload=settings.application.debug)
