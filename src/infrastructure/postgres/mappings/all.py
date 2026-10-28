"""
Single entry point for imperative SQLAlchemy mappings.

Domain entities know nothing about the database: `map_tables()` links them to tables at startup.
Call it in every entrypoint and in alembic `env.py`; repeated calls are safe.
"""

from src.infrastructure.postgres.mappings.outbox import map_outbox_table
from src.infrastructure.postgres.mappings.payment import map_payment_table
from src.infrastructure.postgres.registry import mapper_registry


def map_tables() -> None:
    if mapper_registry.mappers:
        return
    map_payment_table()
    map_outbox_table()
