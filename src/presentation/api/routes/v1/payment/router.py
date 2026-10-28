from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status

from src.application.payment.service import PaymentCreateDTO
from src.domain.payment.vo import PaymentId
from src.presentation.api.routes.v1.deps import IdempotencyKeyDep, PaymentServiceDep, verify_api_key
from src.presentation.api.routes.v1.payment.schemas import (
    PaymentCreateResponseSchema,
    PaymentCreateSchema,
    PaymentResponseSchema,
)

router = APIRouter(
    prefix="/payments", tags=["Payment"], route_class=DishkaRoute, dependencies=[Depends(verify_api_key)]
)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_payment(
    payment: PaymentCreateSchema,
    payment_service: PaymentServiceDep,
    idempotency_key: IdempotencyKeyDep,
) -> PaymentCreateResponseSchema:
    dto = PaymentCreateDTO(**payment.model_dump(), idempotency_key=idempotency_key)
    result = await payment_service.create_payment(dto)
    return PaymentCreateResponseSchema(id=result.id_, status=result.status, created_at=result.created_at)


@router.get("/{payment_id:uuid}", status_code=status.HTTP_200_OK)
async def get_payment(payment_id: UUID, payment_service: PaymentServiceDep) -> PaymentResponseSchema:
    payment = await payment_service.get_payment_by_id(PaymentId(payment_id))
    return PaymentResponseSchema.from_domain(payment)
