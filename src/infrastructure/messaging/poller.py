import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.outbox.interfaces import IMessagePublisher
from src.infrastructure.postgres.repositories import SQLAlchemyOutboxRepository
from src.infrastructure.postgres.transaction_manager import SQLAlchemyTransactionManager

logger = logging.getLogger(__name__)

POLL_INTERVAL = 5.0


class OutboxPoller:
    _polling = False

    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        publisher: IMessagePublisher,
    ) -> None:
        self._sessionmaker = sessionmaker
        self._publisher = publisher

    async def run(self) -> None:
        self._polling = True
        while self._polling:
            try:
                await self._poll_once()
            except Exception:
                logger.exception("Outbox poll cycle failed")
            await asyncio.sleep(POLL_INTERVAL)

    async def _poll_once(self) -> None:
        async with self._sessionmaker() as session:
            outbox_repository = SQLAlchemyOutboxRepository(session)
            transaction_manager = SQLAlchemyTransactionManager(session)
            events = await outbox_repository.get_unpublished()
            for event in events:
                await self._publisher.publish(event)
                event.publish()
                logger.info("Outbox event %s published", event.id_)
            await transaction_manager.commit()

    async def stop(self) -> None:
        self._polling = False
