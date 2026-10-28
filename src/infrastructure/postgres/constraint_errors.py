from collections.abc import Callable, Mapping
from typing import Final

from sqlalchemy.exc import IntegrityError

from src.domain.exceptions.base import AppException
from src.domain.payment.exceptions import PaymentAlreadyExistsError
from src.infrastructure.postgres import constraint_names as cn

CONSTRAINT_TO_ERROR: Final[Mapping[str, Callable[[], AppException]]] = {
    cn.UQ_PAYMENTS_IDEMPOTENCY_KEY: PaymentAlreadyExistsError,
}


def to_domain_error(error: IntegrityError) -> AppException | None:
    message = str(error)
    for name, make_error in CONSTRAINT_TO_ERROR.items():
        if name in message:
            return make_error()
    return None
