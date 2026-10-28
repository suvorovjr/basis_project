from http import HTTPStatus

from src.domain.exceptions.base import AppException


class PaymentAlreadyExistsError(AppException):
    http_status_code = HTTPStatus.CONFLICT

    def __init__(self) -> None:
        super().__init__("Payment with this idempotency key already exists")
