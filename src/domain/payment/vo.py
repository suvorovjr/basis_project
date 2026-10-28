from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import NewType
from uuid import UUID

from src.domain.common import BaseValueObject
from src.domain.exceptions.base import ValidationError

PaymentId = NewType("PaymentId", UUID)


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class Currency(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


@dataclass(frozen=True, slots=True, repr=False)
class Money(BaseValueObject):
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValidationError("Amount must be greater than 0")
        if self.currency not in Currency:
            raise ValidationError("Invalid currency")
