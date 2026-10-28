from fastapi import APIRouter

from src.presentation.api.routes.base import router as base_router
from src.presentation.api.routes.v1 import router as v1_router

router = APIRouter(prefix="/api")

router.include_router(v1_router)
router.include_router(base_router)
