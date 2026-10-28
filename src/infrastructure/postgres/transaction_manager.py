from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.transaction_manager import ITransactionManager
from src.infrastructure.postgres.constraint_errors import to_domain_error


class SQLAlchemyTransactionManager(ITransactionManager):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except IntegrityError as e:
            await self._session.rollback()
            domain_error = to_domain_error(e)
            if domain_error is not None:
                raise domain_error from e
            raise
