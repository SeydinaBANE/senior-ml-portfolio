from enum import StrEnum

from pydantic import BaseModel, Field


class SourceType(StrEnum):
    WEB = "web"
    NOTION = "notion"
    SQL = "sql"


class IngestWebRequest(BaseModel):
    url: str = Field(..., min_length=10)


class IngestSQLRequest(BaseModel):
    connection_url: str
    query: str
    text_columns: list[str]
    source_id: str


class IngestResponse(BaseModel):
    source: str
    chunks_indexed: int
