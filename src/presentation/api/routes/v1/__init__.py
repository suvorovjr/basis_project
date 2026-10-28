from fastapi import APIRouter

from src.presentation.api.routes.v1.payment.router import router as payment_router

router = APIRouter(prefix="/v1")

router.include_router(payment_router)
