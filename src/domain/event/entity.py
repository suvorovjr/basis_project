from __future__ import annotations

from datetime import datetime
from typing import Any, NewType, Self
from uuid import UUID, uuid4

from src.domain.common import BaseEntity, now
from src.domain.exceptions.base import BuisnessLogicError

OutboxId = NewType("OutboxId", UUID)


class Outbox(BaseEntity[OutboxId]):
    def __init__(
        self,
        *,
        id_: OutboxId,
        aggregate_type: str,
        aggregate_id: UUID,
        event_type: str,
        schema_version: int,
        payload: dict[str, Any],
        created_at: datetime,
        published_at: datetime | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self._aggregate_type = aggregate_type
        self._aggregate_id = aggregate_id
        self._event_type = event_type
        self._schema_version = schema_version
        self._payload = payload
        self._created_at = created_at
        self._published_at = published_at

    @classmethod
    def create(
        cls,
        *,
        aggregate_type: str,
        aggregate_id: UUID,
        event_type: str,
        schema_version: int,
        payload: dict[str, Any],
    ) -> Self:
        return cls(
            id_=OutboxId(uuid4()),
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            schema_version=schema_version,
            payload=payload,
            created_at=now(),
            published_at=None,
        )

    @property
    def event_type(self) -> str:
        return self._event_type

    @property
    def payload(self) -> dict[str, Any]:
        return self._payload

    def publish(self) -> None:
        if self._published_at is not None:
            raise BuisnessLogicError("Event is already published")
        self._published_at = now()
