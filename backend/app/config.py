from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="DWCO_", extra="ignore")

    environment: str = "local"
    database_url: str = "postgresql+psycopg://dwco:dwco@postgres:5432/dwco"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = Field(default="local-only-change-me-32-characters-minimum")
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    cors_origins: list[str] = ["http://localhost:3000"]
    auth_rate_limit: int = 10
    mutation_rate_limit: int = 120
    rate_limit_window_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
