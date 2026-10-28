from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.payment.entity import Payment
from src.domain.payment.vo import Currency, PaymentStatus


class PaymentCreateSchema(BaseModel):
    amount: Decimal
    currency: Currency
    description: str
    meta: dict[str, Any] = Field(default_factory=dict)
    webhook_url: str


class PaymentCreateResponseSchema(BaseModel):
    id: UUID
    status: PaymentStatus
    created_at: datetime


class PaymentResponseSchema(BaseModel):
    id: UUID
    amount: Decimal
    currency: Currency
    description: str
    meta: dict[str, Any]
    idempotency_key: UUID
    webhook_url: str
    status: PaymentStatus
    created_at: datetime
    processed_at: datetime | None

    @classmethod
    def from_domain(cls, payment: Payment) -> PaymentResponseSchema:
        return cls(
            id=payment.id_,
            amount=payment.money.amount,
            currency=payment.money.currency,
            description=payment.description,
            meta=payment.meta,
            idempotency_key=payment.idempotency_key,
            webhook_url=payment.webhook_url,
            status=payment.status,
            created_at=payment.created_at,
            processed_at=payment.processed_at,
        )
