from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.payment.entity import Payment
from src.domain.payment.vo import PaymentId


class IPaymentRepository(ABC):
    """Transactional: commit required."""

    @abstractmethod
    def add(self, payment: Payment) -> None: ...

    @abstractmethod
    async def get_by_id(self, payment_id: PaymentId) -> Payment | None: ...

    @abstractmethod
    async def get_by_idempotency_key(self, idempotency_key: UUID) -> Payment | None: ...

    @abstractmethod
    async def get_by_id_and_locked(self, payment_id: PaymentId) -> Payment | None: ...


class IWebhookSender(ABC):
    @abstractmethod
    async def send(self, payment: Payment) -> None: ...
