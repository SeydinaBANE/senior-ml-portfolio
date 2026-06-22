from fastapi import APIRouter

from app.evaluation.ragas_eval import EvalSample, persist_eval_result, run_ragas
from app.rag.pipeline import run_rag
from app.schemas.query import QueryRequest, QueryResponse, SourceReference

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(body: QueryRequest) -> QueryResponse:
    answer, chunks, iterations = await run_rag(body.question)

    sources = [SourceReference(source=c.source, score=round(c.score, 4)) for c in chunks]
    eval_scores: dict[str, float] | None = None

    if body.evaluate:
        sample = EvalSample(
            question=body.question,
            answer=answer,
            contexts=[c.content for c in chunks],
            ground_truth=body.ground_truth,
        )
        scores_list = run_ragas([sample])
        if scores_list:
            s = scores_list[0]
            eval_scores = {
                "faithfulness": s.faithfulness,
                "answer_relevancy": s.answer_relevancy,
                "context_precision": s.context_precision,
            }
            await persist_eval_result(sample, s, iterations)

    return QueryResponse(
        answer=answer,
        sources=sources,
        retrieval_iterations=iterations,
        eval_scores=eval_scores,
    )
