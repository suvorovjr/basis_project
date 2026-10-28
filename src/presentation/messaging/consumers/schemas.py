from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from src.domain.payment.vo import PaymentStatus


class PaymentCreatedEvent(BaseModel):
    id: UUID
    amount: Decimal
    currency: str
    description: str
    meta: dict[str, Any]
    idempotency_key: UUID
    webhook_url: str
    status: PaymentStatus
    created_at: datetime
    processed_at: datetime | None
