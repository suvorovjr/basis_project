from http import HTTPStatus


class AppException(Exception):
    http_status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ResourceNotFoundError(AppException):
    http_status_code = HTTPStatus.NOT_FOUND


class BuisnessLogicError(AppException):
    http_status_code = HTTPStatus.UNPROCESSABLE_ENTITY


class ValidationError(AppException):
    http_status_code = HTTPStatus.BAD_REQUEST


class NotAuthorizedError(AppException):
    http_status_code = HTTPStatus.UNAUTHORIZED


class IntegrationError(AppException):
    http_status_code = HTTPStatus.BAD_GATEWAY
