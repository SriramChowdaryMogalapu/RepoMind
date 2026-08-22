# backend/tests/test_evaluation.py
from app.evaluation.rag_evaluator import RAGEvaluator, EvalTestCase


def test_rag_evaluator_metrics():
    print("\n[TEST] Verifying RAG evaluation metric calculations...")
    test_cases = [
        EvalTestCase(id="1", query="auth logic", expected_files=["auth.py"]),
        EvalTestCase(id="2", query="db pool", expected_files=["db.py"])
    ]
    retrieved_results = [
        ["auth.py", "main.py"],
        ["config.py", "db.py"]
    ]

    metrics = RAGEvaluator.evaluate_retrieval(test_cases, retrieved_results)
    print(f"[TEST] Evaluator Output -> Hit@1: {metrics.hit_at_1}, Hit@3: {metrics.hit_at_3}, MRR: {metrics.mrr}")

    assert metrics.total_queries == 2
    assert metrics.hit_at_1 == 0.5  # 1 out of 2 has exact file at rank 0
    assert metrics.hit_at_3 == 1.0  # both found within top 3
    assert metrics.mrr == 0.75      # (1/1 + 1/2) / 2 = 0.75
    assert metrics.citation_accuracy == 1.0
    print("[TEST] Metrics math verified correctly.")