from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class ApplicationSettings(BaseConfig):
    title: str = "Basis Project"
    version: str = "1.0.0"
    description: str = "Basis API payments project"
    debug: bool = False
    api_key: str = ""

    model_config = SettingsConfigDict(env_prefix="APPLICATION_")


class PostgresSettings(BaseConfig):
    host: str = "127.0.0.1"
    port: int = 5432
    user: str = "postgres"
    password: str = ""
    database: str = "postgres"
    driver: str = "postgresql+asyncpg"

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    @property
    def url(self) -> URL:
        return URL.create(self.driver, self.user, self.password, self.host, self.port, self.database)


class RabbitMQSettings(BaseConfig):
    host: str = "localhost"
    port: int = 5672
    user: str = "admin"
    password: str = "password"

    exchange_payments: str = "payments"
    queue_payments_created: str = "payments.new"
    queue_payments_dead_letter: str = "payments.new.dead"

    model_config = SettingsConfigDict(env_prefix="RABBITMQ_")

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}"


class WebhookSettings(BaseConfig):
    max_attempts: int = 3
    backoff_base: float = 2.0

    model_config = SettingsConfigDict(env_prefix="WEBHOOK_")


class Settings:
    postgres: PostgresSettings = PostgresSettings()
    application: ApplicationSettings = ApplicationSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    webhook: WebhookSettings = WebhookSettings()


settings = Settings()
