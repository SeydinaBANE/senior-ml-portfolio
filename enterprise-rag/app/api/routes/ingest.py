from fastapi import APIRouter, UploadFile

from app.ingestion.notion import ingest_notion_database
from app.ingestion.pdf import ingest_pdf
from app.ingestion.sql import ingest_sql_table
from app.ingestion.web import ingest_url
from app.schemas.ingest import IngestResponse, IngestSQLRequest, IngestWebRequest
from pathlib import Path
import tempfile

router = APIRouter()


@router.post("/ingest/pdf", response_model=IngestResponse)
async def ingest_pdf_endpoint(file: UploadFile) -> IngestResponse:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)
    count = await ingest_pdf(tmp_path)
    tmp_path.unlink(missing_ok=True)
    return IngestResponse(source="pdf", chunks_indexed=count)


@router.post("/ingest/web", response_model=IngestResponse)
async def ingest_web_endpoint(body: IngestWebRequest) -> IngestResponse:
    count = await ingest_url(body.url)
    return IngestResponse(source="web", chunks_indexed=count)


@router.post("/ingest/notion", response_model=IngestResponse)
async def ingest_notion_endpoint() -> IngestResponse:
    count = await ingest_notion_database()
    return IngestResponse(source="notion", chunks_indexed=count)


@router.post("/ingest/sql", response_model=IngestResponse)
async def ingest_sql_endpoint(body: IngestSQLRequest) -> IngestResponse:
    count = await ingest_sql_table(
        body.connection_url, body.query, body.text_columns, body.source_id
    )
    return IngestResponse(source="sql", chunks_indexed=count)
