import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    embedding: Mapped[list] = mapped_column(Vector(1536))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    contexts: Mapped[list] = mapped_column(JSON, default=list)
    faithfulness: Mapped[float | None] = mapped_column(nullable=True)
    answer_relevancy: Mapped[float | None] = mapped_column(nullable=True)
    context_precision: Mapped[float | None] = mapped_column(nullable=True)
    retrieval_iterations: Mapped[int] = mapped_column(default=1)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
