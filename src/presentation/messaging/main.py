import asyncio
from contextlib import asynccontextmanager, suppress
from typing import AsyncGenerator

import uvicorn
from dishka.async_container import make_async_container
from dishka_faststream import setup_dishka
from faststream import ContextRepo
from faststream.asgi import AsgiFastStream
from faststream.rabbit import RabbitBroker
from faststream.specification import AsyncAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.infrastructure.di import ApplicationContainer
from src.infrastructure.messaging.poller import OutboxPoller
from src.infrastructure.messaging.publisher import RabbitMQPublisher
from src.infrastructure.messaging.topology import setup_topology
from src.infrastructure.postgres.mappings.all import map_tables
from src.presentation.messaging import router

broker = RabbitBroker(settings.rabbitmq.url)


@asynccontextmanager
async def lifespan(_: ContextRepo) -> AsyncGenerator[None, None]:
    await broker.connect()
    await setup_topology(broker)

    engine = create_async_engine(settings.postgres.url)
    session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
    publisher = RabbitMQPublisher(broker)
    poller = OutboxPoller(sessionmaker=session_factory, publisher=publisher)

    task = asyncio.create_task(poller.run())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        await broker.stop()
        await engine.dispose()


def create_app() -> AsgiFastStream:
    map_tables()
    container = make_async_container(ApplicationContainer())
    specification = AsyncAPI()
    app = AsgiFastStream(broker, lifespan=lifespan, specification=specification, asyncapi_path="/asyncapi")
    setup_dishka(container, broker=broker, auto_inject=True)
    broker.include_router(router)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("src.presentation.messaging.main:app", host="0.0.0.0", port=8080, reload=settings.application.debug)
