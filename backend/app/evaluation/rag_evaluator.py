# backend/app/evaluation/rag_evaluator.py
from dataclasses import dataclass

from pydantic import BaseModel


class EvalTestCase(BaseModel):
    id: str
    query: str
    expected_files: list[str]
    expected_symbols: list[str] | None = None


@dataclass
class EvalMetrics:
    total_queries: int
    hit_at_1: float
    hit_at_3: float
    hit_at_5: float
    mrr: float
    precision_at_5: float
    citation_accuracy: float


class RAGEvaluator:
    """
    Measures retrieval recall, precision, and citation grounding metrics.
    """

    @staticmethod
    def evaluate_retrieval(
        test_cases: list[EvalTestCase],
        retrieved_results: list[list[str]],  # List of retrieved file paths per query
    ) -> EvalMetrics:
        total = len(test_cases)
        if total == 0:
            return EvalMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        hits_1 = 0
        hits_3 = 0
        hits_5 = 0
        mrr_sum = 0.0
        precision_5_sum = 0.0
        citation_correct = 0

        for test_case, candidates in zip(test_cases, retrieved_results, strict=False):
            expected = set(test_case.expected_files)

            # Hit@1
            if candidates and any(candidates[0].endswith(exp) for exp in expected):
                hits_1 += 1

            # Hit@3
            top_3 = candidates[:3]
            if any(any(c.endswith(exp) for exp in expected) for c in top_3):
                hits_3 += 1

            # Hit@5
            top_5 = candidates[:5]
            if any(any(c.endswith(exp) for exp in expected) for c in top_5):
                hits_5 += 1

            # MRR (Mean Reciprocal Rank)
            rank = None
            for idx, candidate in enumerate(candidates):
                if any(candidate.endswith(exp) for exp in expected):
                    rank = idx + 1
                    break
            if rank:
                mrr_sum += 1.0 / rank

            # Precision@5
            relevant_in_top_5 = sum(1 for c in top_5 if any(c.endswith(exp) for exp in expected))
            precision_5_sum += (relevant_in_top_5 / min(len(top_5), 5)) if top_5 else 0.0

            # Citation correctness
            if relevant_in_top_5 > 0:
                citation_correct += 1

        return EvalMetrics(
            total_queries=total,
            hit_at_1=round(hits_1 / total, 3),
            hit_at_3=round(hits_3 / total, 3),
            hit_at_5=round(hits_5 / total, 3),
            mrr=round(mrr_sum / total, 3),
            precision_at_5=round(precision_5_sum / total, 3),
            citation_accuracy=round(citation_correct / total, 3),
        )
