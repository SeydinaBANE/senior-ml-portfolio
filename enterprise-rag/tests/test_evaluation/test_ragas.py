from unittest.mock import MagicMock, patch

import pytest

from app.evaluation.ragas_eval import EvalSample, EvalScores, run_ragas


def test_run_ragas_returns_scores() -> None:
    sample = EvalSample(
        question="What is X?",
        answer="X is Y.",
        contexts=["X is Y according to source A."],
        ground_truth="X is Y.",
    )

    mock_df = MagicMock()
    mock_df.iterrows.return_value = iter(
        [(0, {"faithfulness": 0.9, "answer_relevancy": 0.85, "context_precision": 0.88})]
    )
    mock_result = MagicMock()
    mock_result.to_pandas.return_value = mock_df

    with patch("app.evaluation.ragas_eval.evaluate", return_value=mock_result):
        scores = run_ragas([sample])

    assert len(scores) == 1
    assert scores[0].faithfulness == 0.9
    assert scores[0].answer_relevancy == 0.85
