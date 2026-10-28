import asyncio
import logging
import random

from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.payment.interfaces import IPaymentRepository, IWebhookSender
from src.domain.exceptions.base import BuisnessLogicError, ResourceNotFoundError
from src.domain.payment.vo import PaymentId

logger = logging.getLogger(__name__)

PROCESSING_TIME_MIN = 2.0
PROCESSING_TIME_MAX = 5.0
SUCCESS_RATE = 0.9


class PaymentGateway:
    def __init__(
        self,
        payment_repository: IPaymentRepository,
        transaction_manager: ITransactionManager,
        webhook_sender: IWebhookSender,
    ) -> None:
        self._payment_repository = payment_repository
        self._transaction_manager = transaction_manager
        self._webhook_sender = webhook_sender

    async def process_payment(self, payment_id: PaymentId) -> None:
        processing_time = random.uniform(PROCESSING_TIME_MIN, PROCESSING_TIME_MAX)
        await asyncio.sleep(processing_time)
        payment = await self._payment_repository.get_by_id_and_locked(payment_id)
        if not payment:
            logger.warning("Payment with id %s not found", payment_id)
            raise ResourceNotFoundError(f"Payment with id {payment_id} not found")
        if payment.processed_at is not None:
            logger.warning("Payment with id %s already processed", payment_id)
            raise BuisnessLogicError(f"Payment with id {payment_id} already processed")
        if random.random() < SUCCESS_RATE:
            payment.mark_succeeded()
        else:
            payment.mark_failed()
        await self._transaction_manager.commit()
        await self._webhook_sender.send(payment)
        logger.info("Payment with id %s processed", payment_id)
