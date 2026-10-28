from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.outbox.interfaces import IOutboxRepository
from src.application.payment.gateway import PaymentGateway
from src.application.payment.interfaces import IPaymentRepository, IWebhookSender
from src.application.payment.service import PaymentService
from src.core.config import settings
from src.infrastructure.http.webhook_sender import HTTPWebhookSender
from src.infrastructure.postgres.repositories import SQLAlchemyOutboxRepository, SQLAlchemyPaymentRepository
from src.infrastructure.postgres.transaction_manager import SQLAlchemyTransactionManager


class ApplicationContainer(Provider):
    @provide(scope=Scope.APP)
    async def engine(self) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(settings.postgres.url)
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.APP)
    def sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.APP)
    async def http_client(self) -> AsyncIterable[AsyncClient]:
        async with AsyncClient() as client:
            yield client

    @provide(scope=Scope.APP)
    def webhook_sender(self, client: AsyncClient) -> IWebhookSender:
        return HTTPWebhookSender.from_settings(client)

    @provide(scope=Scope.REQUEST)
    async def db_session(self, sessionmaker: async_sessionmaker) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def transaction_manager(self, db_session: AsyncSession) -> ITransactionManager:
        return SQLAlchemyTransactionManager(db_session)

    @provide(scope=Scope.REQUEST)
    def payment_repository(self, db_session: AsyncSession) -> IPaymentRepository:
        return SQLAlchemyPaymentRepository(db_session)

    @provide(scope=Scope.REQUEST)
    def outbox_repository(self, db_session: AsyncSession) -> IOutboxRepository:
        return SQLAlchemyOutboxRepository(db_session)

    @provide(scope=Scope.REQUEST)
    def payment_service(
        self,
        payment_repository: IPaymentRepository,
        outbox_repository: IOutboxRepository,
        transaction_manager: ITransactionManager,
    ) -> PaymentService:
        return PaymentService(payment_repository, outbox_repository, transaction_manager)

    @provide(scope=Scope.REQUEST)
    def payment_gateway(
        self,
        payment_repository: IPaymentRepository,
        transaction_manager: ITransactionManager,
        webhook_sender: IWebhookSender,
    ) -> PaymentGateway:
        return PaymentGateway(payment_repository, transaction_manager, webhook_sender)
