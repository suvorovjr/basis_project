from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar
from uuid import UUID, uuid4

from src.domain.common import BaseEntity, now
from src.domain.exceptions.base import BuisnessLogicError
from src.domain.payment.vo import Money, PaymentId, PaymentStatus


class Payment(BaseEntity[PaymentId]):
    _ALLOWED_STATUS_TRANSITIONS: ClassVar[dict[PaymentStatus, set[PaymentStatus]]] = {
        PaymentStatus.PENDING: {PaymentStatus.SUCCEEDED, PaymentStatus.FAILED},
        PaymentStatus.SUCCEEDED: set(),
        PaymentStatus.FAILED: set(),
    }

    def __init__(
        self,
        *,
        id_: PaymentId,
        money: Money,
        description: str,
        meta: dict[str, Any] | None = None,
        idempotency_key: UUID,
        webhook_url: str,
        status: PaymentStatus,
        created_at: datetime,
        processed_at: datetime | None,
    ) -> None:
        super().__init__(id_=id_)
        self._money = money
        self._description = description
        self._meta = dict(meta) if meta is not None else {}
        self._idempotency_key = idempotency_key
        self._webhook_url = webhook_url
        self._status = status
        self._created_at = created_at
        self._processed_at = processed_at

    @classmethod
    def create(
        cls,
        *,
        money: Money,
        description: str,
        meta: dict[str, Any] | None = None,
        idempotency_key: UUID,
        webhook_url: str,
    ) -> Payment:
        return cls(
            id_=PaymentId(uuid4()),
            money=money,
            description=description,
            meta=meta,
            idempotency_key=idempotency_key,
            webhook_url=webhook_url,
            status=PaymentStatus.PENDING,
            created_at=now(),
            processed_at=None,
        )

    @property
    def money(self) -> Money:
        return self._money

    @property
    def description(self) -> str:
        return self._description

    @property
    def meta(self) -> dict[str, Any]:
        return dict(self._meta)

    @property
    def idempotency_key(self) -> UUID:
        return self._idempotency_key

    @property
    def webhook_url(self) -> str:
        return self._webhook_url

    @property
    def status(self) -> PaymentStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def processed_at(self) -> datetime | None:
        return self._processed_at

    def mark_succeeded(self) -> None:
        self._transition_status(PaymentStatus.SUCCEEDED)
        self._processed_at = now()

    def mark_failed(self) -> None:
        self._transition_status(PaymentStatus.FAILED)
        self._processed_at = now()

    def _transition_status(self, status: PaymentStatus) -> None:
        if self._status in (PaymentStatus.SUCCEEDED, PaymentStatus.FAILED):
            raise BuisnessLogicError("Payment is already in a final state")
        if status not in self._ALLOWED_STATUS_TRANSITIONS[self._status]:
            raise BuisnessLogicError("Invalid status transition")
        self._status = status

    def to_payload_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id_),
            "amount": str(self._money.amount),
            "currency": self._money.currency.value,
            "description": self._description,
            "meta": self._meta,
            "idempotency_key": str(self._idempotency_key),
            "webhook_url": self._webhook_url,
            "status": self._status.value,
            "created_at": self._created_at.isoformat(),
            "processed_at": self._processed_at.isoformat() if self._processed_at else None,
        }
