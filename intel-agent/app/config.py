from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    openai_api_key: str
    openai_model: str = "gpt-4o"
    llm_api_base: str = ""
    llm_api_key: str = ""
    llm_model_primary: str = "gpt-4o"
    llm_model_fallback: str = "gpt-4o-mini"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "intel-agent"

    metrics_port: int = 9090

    rate_limit_max_requests: int = 100
    rate_limit_window_sec: int = 60
    api_key_mapping: dict[str, str] = {}


settings = Settings()  # type: ignore[call-arg]
