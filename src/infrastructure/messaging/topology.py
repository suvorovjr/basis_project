from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from src.core.config import settings

PAYMENTS_EXCHANGE = RabbitExchange(settings.rabbitmq.exchange_payments, type=ExchangeType.DIRECT, durable=True)
PAYMENTS_CREATED_QUEUE = RabbitQueue(
    settings.rabbitmq.queue_payments_created,
    routing_key=settings.rabbitmq.queue_payments_created,
    durable=True,
    arguments={
        "x-dead-letter-exchange": settings.rabbitmq.exchange_payments,
        "x-dead-letter-routing-key": settings.rabbitmq.queue_payments_dead_letter,
    },
)
PAYMENTS_DEAD_LETTER_QUEUE = RabbitQueue(
    settings.rabbitmq.queue_payments_dead_letter,
    routing_key=settings.rabbitmq.queue_payments_dead_letter,
    durable=True,
)


async def setup_topology(broker: RabbitBroker) -> None:
    payments_exchange = await broker.declare_exchange(PAYMENTS_EXCHANGE)
    await broker.declare_queue(PAYMENTS_CREATED_QUEUE)
    payment_dead_letter_queue = await broker.declare_queue(PAYMENTS_DEAD_LETTER_QUEUE)
    await payment_dead_letter_queue.bind(payments_exchange, routing_key=settings.rabbitmq.queue_payments_dead_letter)
