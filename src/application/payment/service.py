import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID

from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.outbox.interfaces import IOutboxRepository
from src.application.payment.interfaces import IPaymentRepository
from src.domain.exceptions.base import ResourceNotFoundError
from src.domain.payment.entity import Payment
from src.domain.payment.events import payment_created
from src.domain.payment.exceptions import PaymentAlreadyExistsError
from src.domain.payment.vo import Currency, Money, PaymentId

logger = logging.getLogger(__name__)


@dataclass
class PaymentCreateDTO:
    amount: Decimal
    currency: Currency
    description: str
    meta: dict[str, Any]
    idempotency_key: UUID
    webhook_url: str

    def to_payment(self) -> Payment:
        return Payment.create(
            money=Money(amount=self.amount, currency=self.currency),
            description=self.description,
            meta=self.meta,
            idempotency_key=self.idempotency_key,
            webhook_url=self.webhook_url,
        )


class PaymentService:
    def __init__(
        self,
        payment_repository: IPaymentRepository,
        outbox_repository: IOutboxRepository,
        transaction_manager: ITransactionManager,
    ) -> None:
        self._payment_repository = payment_repository
        self._outbox_repository = outbox_repository
        self._transaction_manager = transaction_manager

    async def create_payment(self, payment: PaymentCreateDTO) -> Payment:
        new_payment = payment.to_payment()
        existing_payment = await self._payment_repository.get_by_idempotency_key(new_payment.idempotency_key)
        if existing_payment:
            return existing_payment
        self._payment_repository.add(new_payment)
        self._outbox_repository.add(payment_created(new_payment))
        try:
            await self._transaction_manager.commit()
        except PaymentAlreadyExistsError:
            existing_payment = await self._payment_repository.get_by_idempotency_key(new_payment.idempotency_key)
            if existing_payment is None:
                raise
            return existing_payment
        return new_payment

    async def get_payment_by_id(self, payment_id: PaymentId) -> Payment:
        payment = await self._payment_repository.get_by_id(payment_id)
        if not payment:
            logger.warning("Payment with id %s not found", payment_id)
            raise ResourceNotFoundError(f"Payment with id {payment_id} not found")
        return payment
