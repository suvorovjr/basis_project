from src.domain.event.entity import Outbox
from src.domain.payment.entity import Payment

PAYMENT_AGGREGATE_TYPE = "Payment"
PAYMENT_CREATED_EVENT_TYPE = "payments.new"
PAYMENT_CREATED_SCHEMA_VERSION = 1


def payment_created(payment: Payment) -> Outbox:
    return Outbox.create(
        aggregate_type=PAYMENT_AGGREGATE_TYPE,
        aggregate_id=payment.id_,
        event_type=PAYMENT_CREATED_EVENT_TYPE,
        schema_version=PAYMENT_CREATED_SCHEMA_VERSION,
        payload=payment.to_payload_dict(),
    )
