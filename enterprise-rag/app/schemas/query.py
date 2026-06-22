from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)
    evaluate: bool = False
    ground_truth: str = ""


class SourceReference(BaseModel):
    source: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
    retrieval_iterations: int
    eval_scores: dict[str, float] | None = None
