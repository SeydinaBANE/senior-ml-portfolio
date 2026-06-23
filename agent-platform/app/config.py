from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str
    api_v1_prefix: str = "/api/v1"

    openai_api_key: str
    openai_model: str = "gpt-4o"

    database_url: str
    database_url_sync: str

    redis_url: str = "redis://localhost:6379/0"

    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    price_per_1k_input_tokens: float = 0.005
    price_per_1k_output_tokens: float = 0.015

    otlp_endpoint: str = "http://localhost:4317"
    metrics_port: int = 9090
    rate_limit_max_requests: int = 100
    rate_limit_window_sec: int = 60
    api_key_mapping: dict[str, str] = {}


settings = Settings()  # type: ignore[call-arg]
