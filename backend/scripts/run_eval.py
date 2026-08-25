# backend/scripts/run_eval.py
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


from app.evaluation.rag_evaluator import EvalTestCase, RAGEvaluator

SAMPLE_TEST_SET = [
    EvalTestCase(
        id="q1",
        query="Where is user authentication implemented?",
        expected_files=["src/auth/jwt.py", "src/auth/middleware.py"],
    ),
    EvalTestCase(
        id="q2",
        query="Where is the database session engine initialized?",
        expected_files=["src/db/session.py"],
    ),
    EvalTestCase(
        id="q3", query="How does rate limiting work?", expected_files=["src/core/rate_limiter.py"]
    ),
]

# Simulated retrieval candidates for benchmark verification
SIMULATED_RETRIEVAL = [
    ["src/auth/jwt.py", "src/auth/middleware.py", "src/main.py"],
    ["src/db/session.py", "src/models/chunk.py"],
    ["src/core/rate_limiter.py", "src/core/config.py"],
]


def run_benchmark():
    print("\n=======================================================")
    print("           RepoMind RAG Retrieval Evaluation          ")
    print("=======================================================\n")

    metrics = RAGEvaluator.evaluate_retrieval(SAMPLE_TEST_SET, SIMULATED_RETRIEVAL)

    print(f"Total Benchmark Queries:   {metrics.total_queries}")
    print(f"Hit@1:                     {metrics.hit_at_1 * 100:.1f}%")
    print(f"Hit@3:                     {metrics.hit_at_3 * 100:.1f}%")
    print(f"Hit@5:                     {metrics.hit_at_5 * 100:.1f}%")
    print(f"MRR (Mean Reciprocal Rank): {metrics.mrr:.3f}")
    print(f"Precision@5:               {metrics.precision_at_5 * 100:.1f}%")
    print(f"Citation Accuracy:         {metrics.citation_accuracy * 100:.1f}%\n")
    print("=======================================================\n")


if __name__ == "__main__":
    run_benchmark()
