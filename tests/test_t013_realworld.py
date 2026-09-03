"""T013 Real-World News Quality Regression Tests"""

import pytest
from pathlib import Path
from world_news.quality import RealWorldEvaluator


def test_real_world_evaluator_summary():
    """Test RealWorldEvaluator CLI runner with 204 real-world reviewed items"""
    review_path = Path("docs/t013/review.json")
    assert review_path.exists(), "docs/t013/review.json must exist"

    evaluator = RealWorldEvaluator(review_path)
    metrics = evaluator.evaluate()

    assert metrics["total_articles"] >= 100
    assert metrics["reviewed"] >= 100
    assert metrics["country_accuracy"] >= 0.90
    assert metrics["location_accuracy"] >= 0.90
    assert metrics["critical_errs"] == 0


def test_t013_error_report_file_exists():
    """Test that docs/t013/errors.md error taxonomy report file is present"""
    err_path = Path("docs/t013/errors.md")
    assert err_path.exists(), "docs/t013/errors.md must exist"
    content = err_path.read_text(encoding="utf-8")
    assert "# T013 Error Taxonomy" in content
