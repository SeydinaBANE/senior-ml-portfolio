from dataclasses import dataclass

from app.db.models import EvaluationResult
from app.db.session import async_session


@dataclass
class EvalSample:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str = ""


@dataclass
class EvalScores:
    faithfulness: float
    answer_relevancy: float
    context_precision: float


def run_ragas(samples: list[EvalSample]) -> list[EvalScores]:
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import answer_relevancy, context_precision, faithfulness

    dataset = Dataset.from_list(
        [
            {
                "question": s.question,
                "answer": s.answer,
                "contexts": s.contexts,
                "ground_truth": s.ground_truth,
            }
            for s in samples
        ]
    )
    results = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
    )
    df = results.to_pandas()
    return [
        EvalScores(
            faithfulness=row["faithfulness"],
            answer_relevancy=row["answer_relevancy"],
            context_precision=row["context_precision"],
        )
        for _, row in df.iterrows()
    ]


async def persist_eval_result(
    sample: EvalSample, scores: EvalScores, retrieval_iterations: int
) -> None:
    async with async_session() as db:
        db.add(
            EvaluationResult(
                question=sample.question,
                answer=sample.answer,
                contexts=sample.contexts,
                faithfulness=scores.faithfulness,
                answer_relevancy=scores.answer_relevancy,
                context_precision=scores.context_precision,
                retrieval_iterations=retrieval_iterations,
            )
        )
        await db.commit()
