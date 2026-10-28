from typing import Final

import sqlalchemy as sa

from src.domain.event.entity import Outbox
from src.infrastructure.postgres.registry import mapper_registry

MAX_LENGTH_STRING = 255
IX_OUTBOX_UNPUBLISHED: Final[str] = "ix_outbox_unpublished"

outbox_table = sa.Table(
    "outbox",
    mapper_registry.metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("aggregate_type", sa.String(MAX_LENGTH_STRING), nullable=False),
    sa.Column("aggregate_id", sa.UUID(as_uuid=True), nullable=False),
    sa.Column("event_type", sa.String(MAX_LENGTH_STRING), nullable=False),
    sa.Column("schema_version", sa.SmallInteger, nullable=False, server_default="1"),
    sa.Column("payload", sa.JSON, nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
    sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
)

sa.Index(
    IX_OUTBOX_UNPUBLISHED,
    outbox_table.c.published_at,
    postgresql_where=outbox_table.c.published_at.is_(None),
)


def map_outbox_table() -> None:
    mapper_registry.map_imperatively(
        Outbox,
        outbox_table,
        properties={
            "id_": outbox_table.c.id,
            "_aggregate_type": outbox_table.c.aggregate_type,
            "_aggregate_id": outbox_table.c.aggregate_id,
            "_event_type": outbox_table.c.event_type,
            "_schema_version": outbox_table.c.schema_version,
            "_payload": outbox_table.c.payload,
            "_created_at": outbox_table.c.created_at,
            "_published_at": outbox_table.c.published_at,
        },
        column_prefix="__",
    )
