from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.outbox.interfaces import IOutboxRepository
from src.application.payment.interfaces import IPaymentRepository
from src.domain.event.entity import Outbox
from src.domain.payment.entity import Payment
from src.domain.payment.vo import PaymentId
from src.infrastructure.postgres.mappings.outbox import outbox_table
from src.infrastructure.postgres.mappings.payment import payment_table


class SQLAlchemyPaymentRepository(IPaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, payment: Payment) -> None:
        self._session.add(payment)

    async def get_by_id(self, payment_id: PaymentId) -> Payment | None:
        query = sa.select(Payment).where(payment_table.c.id == payment_id)
        return (await self._session.execute(query)).scalar_one_or_none()

    async def get_by_idempotency_key(self, idempotency_key: UUID) -> Payment | None:
        query = sa.select(Payment).where(payment_table.c.idempotency_key == idempotency_key)
        return (await self._session.execute(query)).scalar_one_or_none()

    async def get_by_id_and_locked(self, payment_id: PaymentId) -> Payment | None:
        query = sa.select(Payment).where(payment_table.c.id == payment_id).with_for_update(skip_locked=True)
        return (await self._session.execute(query)).scalar_one_or_none()


class SQLAlchemyOutboxRepository(IOutboxRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, event: Outbox) -> None:
        self._session.add(event)

    async def get_unpublished(self) -> list[Outbox]:
        query = sa.select(Outbox).where(outbox_table.c.published_at.is_(None)).with_for_update(skip_locked=True)
        return list((await self._session.execute(query)).scalars().all())
