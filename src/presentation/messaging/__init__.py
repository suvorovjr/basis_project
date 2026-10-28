from faststream.rabbit import RabbitRouter

from src.presentation.messaging.consumers.gateway import router as gateway_router

router = RabbitRouter()
router.include_router(gateway_router)
