import asyncio
import logging
from uuid import uuid4

from httpx import AsyncClient, HTTPError

from src.application.payment.interfaces import IWebhookSender
from src.core.config import settings
from src.domain.exceptions.base import IntegrationError
from src.domain.payment.entity import Payment

logger = logging.getLogger(__name__)


class HTTPWebhookSender(IWebhookSender):
    def __init__(self, client: AsyncClient, max_attempts: int = 3, backoff_base: float = 2.0) -> None:
        self._client = client
        self._max_attempts = max_attempts
        self._backoff_base = backoff_base

    @classmethod
    def from_settings(cls, client: AsyncClient) -> "HTTPWebhookSender":
        return cls(
            client=client,
            max_attempts=settings.webhook.max_attempts,
            backoff_base=settings.webhook.backoff_base,
        )

    async def send(self, payment: Payment) -> None:
        payload = payment.to_payload_dict()
        headers = self._build_headers(payment)
        last_exc: HTTPError | None = None

        for attempt in range(1, self._max_attempts + 1):
            try:
                response = await self._client.post(payment.webhook_url, json=payload, headers=headers)
                response.raise_for_status()
                logger.info("Webhook delivered for payment %s on attempt %d", payment.id_, attempt)
                return
            except HTTPError as exc:
                last_exc = exc
                logger.warning(
                    "Webhook attempt %d/%d failed for payment %s: %s", attempt, self._max_attempts, payment.id_, exc
                )
                if attempt < self._max_attempts:
                    await asyncio.sleep(self._backoff_base**attempt)

        logger.error("Webhook delivery failed after %d attempts for payment %s", self._max_attempts, payment.id_)
        raise IntegrationError(f"Webhook delivery failed for payment {payment.id_}") from last_exc

    def _build_headers(self, payment: Payment) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Delivery-Id": uuid4().hex,
            "X-Idempotency-Key": str(payment.idempotency_key),
        }
