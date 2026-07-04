from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AidBot"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://aidbot:aidbot_dev_password@localhost:5432/aidbot"
    backend_cors_origins: str = Field(default="http://localhost:3010,http://127.0.0.1:3010")
    auth_secret_key: str = "change-this-dev-secret"
    auth_token_ttl_seconds: int = 28800
    seed_admin_email: str = "admin@aidbot.local"
    seed_admin_password: str = "aidbot123"
    seed_admin_name: str = "售后管理员"
    llm_provider: str = "local"
    llm_model: str = "aidbot-local-v1"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_timeout_seconds: float = 60.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
