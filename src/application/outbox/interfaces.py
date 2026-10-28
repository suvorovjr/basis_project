from abc import ABC, abstractmethod

from src.domain.event.entity import Outbox


class IOutboxRepository(ABC):
    """Transactional: commit required."""

    @abstractmethod
    def add(self, event: Outbox) -> None: ...

    @abstractmethod
    async def get_unpublished(self) -> list[Outbox]: ...


class IMessagePublisher(ABC):
    @abstractmethod
    async def publish(self, event: Outbox) -> None: ...
