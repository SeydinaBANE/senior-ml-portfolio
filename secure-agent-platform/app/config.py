from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str
    api_v1_prefix: str = "/api/v1"

    openai_api_key: str
    openai_model: str = "gpt-4o"
    llm_api_base: str = ""
    llm_api_key: str = ""
    llm_model_primary: str = "gpt-4o"
    llm_model_fallback: str = "gpt-4o-mini"

    database_url: str
    database_url_sync: str

    redis_url: str = "redis://localhost:6379/0"

    opa_url: str = "http://localhost:8181"

    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    metrics_port: int = 9090
    rate_limit_max_requests: int = 100
    rate_limit_window_sec: int = 60
    api_key_mapping: dict[str, str] = {}


settings = Settings()  # type: ignore[call-arg]
