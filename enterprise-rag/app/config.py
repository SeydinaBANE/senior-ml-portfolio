from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    openai_api_key: str
    openai_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"

    database_url: str
    database_url_sync: str

    notion_api_key: str = ""
    notion_database_id: str = ""

    max_retrieval_iterations: int = 3
    top_k_chunks: int = 6
    bm25_weight: float = 0.4
    vector_weight: float = 0.6


settings = Settings()  # type: ignore[call-arg]
