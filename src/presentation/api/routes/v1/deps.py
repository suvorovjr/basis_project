from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import Header, HTTPException, status
from fastapi.security import APIKeyHeader

from src.application.payment.service import PaymentService
from src.core.config import settings

PaymentServiceDep = Annotated[PaymentService, Depends()]
IdempotencyKeyDep = Annotated[UUID, Header(alias="Idempotency-Key")]

api_key_schema = APIKeyHeader(name="X-Api-Key", auto_error=False)


def verify_api_key(api_key: Annotated[str | None, Depends(api_key_schema)]) -> None:
    if api_key != settings.application.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
