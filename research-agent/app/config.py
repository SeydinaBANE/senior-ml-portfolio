from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    openai_api_key: str
    openai_model: str = "gpt-4o"

    tavily_api_key: str = ""

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    google_token_path: str = ".secrets/google_token.json"

    notion_api_key: str = ""

    slack_bot_token: str = ""
    slack_default_channel: str = "#research-reports"

    max_search_queries: int = 5
    max_sources_per_query: int = 3
    min_source_confidence: float = 0.6


settings = Settings()  # type: ignore[call-arg]
