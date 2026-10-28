from abc import ABC, abstractmethod


class ITransactionManager(ABC):
    """
    UoW-compatible interface for committing a business transaction.
    The implementation is an ORM session: repositories add entities to it,
    loaded entities are tracked by it, and `commit()` writes all their changes.
    Uncommitted changes are rolled back when the session is closed.
    A violated business constraint is rolled back and raised as a domain error.
    """

    @abstractmethod
    async def commit(self) -> None: ...
