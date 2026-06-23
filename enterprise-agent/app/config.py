from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEV_SECRET = "dev-secret-key-change-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = _DEV_SECRET
    api_v1_prefix: str = "/api/v1"

    openai_api_key: str = "sk-test"
    openai_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/enterprise_agent"
    )
    database_url_sync: str = (
        "postgresql://postgres:postgres@localhost:5432/enterprise_agent"
    )

    redis_url: str = "redis://localhost:6379/0"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    rate_limit_max_requests: int = 100
    rate_limit_window_sec: int = 60
    api_key_mapping: dict[str, str] = {}

    @model_validator(mode="after")
    def validate_production_config(self) -> "Settings":
        if self.app_env == "production":
            if self.secret_key == _DEV_SECRET:
                raise ValueError("SECRET_KEY must be overridden in production")
            if not self.openai_api_key.startswith("sk-") or self.openai_api_key == "sk-test":
                raise ValueError("OPENAI_API_KEY must be a real key in production")
        return self


settings = Settings()  # type: ignore[call-arg]
