import logging
from typing import Annotated

from dishka_faststream import FromDishka
from faststream.rabbit import RabbitRouter

from src.application.payment.gateway import PaymentGateway
from src.domain.exceptions.base import BuisnessLogicError, IntegrationError
from src.domain.payment.vo import PaymentId
from src.infrastructure.messaging.topology import PAYMENTS_CREATED_QUEUE, PAYMENTS_EXCHANGE
from src.presentation.messaging.consumers.schemas import PaymentCreatedEvent

logger = logging.getLogger(__name__)

router = RabbitRouter(include_in_schema=True)


@router.subscriber(PAYMENTS_CREATED_QUEUE, exchange=PAYMENTS_EXCHANGE)
async def payment_created(
    message: PaymentCreatedEvent,
    gateway: Annotated[PaymentGateway, FromDishka()],
) -> None:
    payment_id = PaymentId(message.id)
    logger.info("Processing payment %s", payment_id)
    try:
        await gateway.process_payment(payment_id)
    except (IntegrationError, BuisnessLogicError) as e:
        logger.error("Error processing payment %s: %s", payment_id, e)
        raise e
