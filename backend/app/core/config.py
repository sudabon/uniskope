"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/uniskope"

    # API
    api_key: str | None = None
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Webhook secrets (provider-specific)
    stripe_webhook_secret: str | None = None
    lemonsqueezy_webhook_secret: str | None = None
    paddle_webhook_secret: str | None = None


settings = Settings()
