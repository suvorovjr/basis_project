import sqlalchemy as sa
from sqlalchemy.orm import composite

from src.domain.payment.entity import Payment
from src.domain.payment.vo import Currency, Money, PaymentStatus
from src.infrastructure.postgres.constraint_names import UQ_PAYMENTS_IDEMPOTENCY_KEY
from src.infrastructure.postgres.mappings.support import get_strenum_values
from src.infrastructure.postgres.registry import mapper_registry

MAX_LENGTH_STRING = 255

payment_table = sa.Table(
    "payments",
    mapper_registry.metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("amount", sa.DECIMAL(precision=18, scale=4), nullable=False),
    sa.Column(
        "currency",
        sa.Enum(
            Currency,
            native_enum=False,
            length=MAX_LENGTH_STRING,
            validate_strings=True,
            values_callable=get_strenum_values,
        ),
        nullable=False,
    ),
    sa.Column("description", sa.String(MAX_LENGTH_STRING), nullable=False),
    sa.Column("meta", sa.JSON, nullable=False),
    sa.Column("idempotency_key", sa.UUID(as_uuid=True), nullable=False),
    sa.Column("webhook_url", sa.String(MAX_LENGTH_STRING), nullable=False),
    sa.Column(
        "status",
        sa.Enum(
            PaymentStatus,
            native_enum=False,
            length=MAX_LENGTH_STRING,
            validate_strings=True,
            values_callable=get_strenum_values,
        ),
        nullable=False,
    ),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
    sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
)

sa.Index(UQ_PAYMENTS_IDEMPOTENCY_KEY, payment_table.c.idempotency_key, unique=True)


def map_payment_table() -> None:
    mapper_registry.map_imperatively(
        Payment,
        payment_table,
        properties={
            "id_": payment_table.c.id,
            "_money": composite(Money, payment_table.c.amount, payment_table.c.currency),
            "_description": payment_table.c.description,
            "_meta": payment_table.c.meta,
            "_idempotency_key": payment_table.c.idempotency_key,
            "_webhook_url": payment_table.c.webhook_url,
            "_status": payment_table.c.status,
            "_created_at": payment_table.c.created_at,
            "_processed_at": payment_table.c.processed_at,
        },
        column_prefix="__",
    )
