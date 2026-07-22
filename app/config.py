"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field("Inventory Platform API", env="APP_NAME")
    app_version: str = Field("1.0.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")

    database_url: str = Field(..., env="DATABASE_URL")
    sync_database_url: str = Field(..., env="SYNC_DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    celery_broker_url: str = Field("redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field("redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")

    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES", ge=5)
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS", ge=1)

    allowed_origins_raw: str = Field("", env="ALLOWED_ORIGINS")
    run_migrations: bool = Field(False, env="RUN_MIGRATIONS")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    cache_ttl_seconds: int = Field(300, env="CACHE_TTL_SECONDS", ge=60)
    audit_retention_days: int = Field(365, env="AUDIT_RETENTION_DAYS", ge=30)
    max_page_size: int = Field(100, env="MAX_PAGE_SIZE", ge=10, le=500)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("allowed_origins_raw", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str] | tuple[str, ...] | None) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, (list, tuple)):
            return ",".join(str(v).strip() for v in value if str(v).strip())
        raise TypeError("ALLOWED_ORIGINS must be comma-separated string or list")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
