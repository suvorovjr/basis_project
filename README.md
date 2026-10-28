# Тестовое задание — МКК Базис - Асинхронный сервис процессинга платежей.

## Стек

- **FastAPI** + Pydantic v2
- **SQLAlchemy 2.0** (async) + PostgreSQL
- **RabbitMQ** + FastStream
- **Alembic** — миграции
- **Dishka** — dependency injection
- **Docker** + docker-compose

## Поток обработки платежа:
1. `POST /api/v1/payments` создаёт платёж и Outbox-запись в одной транзакции
2. Outbox poller публикует событие в RabbitMQ очередь `payments.new`
3. Consumer получает сообщение, эмулирует обработку (2–5 сек, 90% успех), обновляет статус и отправляет webhook
4. При 3 неудачных попытках отправки уходит в Dead Letter Queue

## Запуск

### 1. Переменные окружения

```bash
cp .env.example .env
```

При необходимости отредактируй `.env`.

### 2. Запуск через Docker

```bash
docker-compose up --build
```
