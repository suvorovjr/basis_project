import logging

from faststream.rabbit import RabbitBroker

from src.application.outbox.interfaces import IMessagePublisher
from src.domain.event.entity import Outbox
from src.infrastructure.messaging.topology import PAYMENTS_EXCHANGE

logger = logging.getLogger(__name__)


class RabbitMQPublisher(IMessagePublisher):
    def __init__(self, broker: RabbitBroker) -> None:
        self._broker = broker

    async def publish(self, event: Outbox) -> None:
        await self._broker.publish(
            event.payload,
            exchange=PAYMENTS_EXCHANGE,
            routing_key=event.event_type,
        )
        logger.debug("Published outbox event %s (type=%s)", event.id_, event.event_type)
