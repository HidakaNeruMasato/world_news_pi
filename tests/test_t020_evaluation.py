"""Unit tests for T020 Evaluator and Human Review Analysis (T020 Phase 3)."""

import os
import json
import pytest
from pathlib import Path
from world_news.quality_evaluator import T020Evaluator


def test_evaluator_initialization_defaults():
    evaluator = T020Evaluator()
    assert evaluator.review_results_path == "docs/t020/review_results.json"
    assert evaluator.dataset_path == "docs/t020/dataset.json"


def test_evaluator_review_status():
    evaluator = T020Evaluator()
    st = evaluator.get_review_status()
    assert st["total_events"] == 150
    assert st["reviewed"] == 150
    assert st["remaining"] == 0
    assert st["completion_rate"] == 100.0
    assert st["invalid_reviews"] == 0
    assert st["critical_errors"] == 0


def test_evaluator_summary_metrics():
    evaluator = T020Evaluator()
    summary = evaluator.compute_summary_metrics()
    assert summary["review_count"] == 150
    assert "average_scores" in summary
    assert "rates" in summary
    assert "location" in summary
    assert summary["critical_errors"] == 0
    assert summary["verdict"] in ["PASS", "CONDITIONAL PASS", "FAIL"]


def test_evaluator_map_user_value_rate_calculation():
    evaluator = T020Evaluator()
    summary = evaluator.compute_summary_metrics()
    rate = summary["rates"]["map_user_value_rate"]
    assert 0.0 <= rate <= 100.0
    assert summary["verdict"] == "PASS" if rate >= 70.0 and summary["critical_errors"] == 0 else True


def test_evaluator_regional_breakdown():
    evaluator = T020Evaluator()
    regions = evaluator.compute_regional_breakdown()
    assert isinstance(regions, dict)
    assert len(regions) >= 4
    for reg, stats in regions.items():
        assert "event_count" in stats
        assert "user_value_rate" in stats
        assert "average_map_value" in stats
        assert "average_would_view" in stats


def test_evaluator_country_breakdown():
    evaluator = T020Evaluator()
    countries = evaluator.compute_country_breakdown()
    assert isinstance(countries, dict)
    assert len(countries) >= 5
    for cntry, stats in countries.items():
        assert "small_sample" in stats
        assert stats["small_sample"] == (stats["event_count"] < 3)


def test_evaluator_source_breakdown():
    evaluator = T020Evaluator()
    sources = evaluator.compute_source_breakdown()
    assert isinstance(sources, dict)
    assert len(sources) >= 5
    for sname, stats in sources.items():
        assert "insufficient_sample" in stats
        assert stats["insufficient_sample"] == (stats["event_count"] < 5)


def test_evaluator_category_breakdown():
    evaluator = T020Evaluator()
    categories = evaluator.compute_category_breakdown()
    assert isinstance(categories, dict)
    assert len(categories) >= 3


def test_evaluator_cross_border_analysis():
    evaluator = T020Evaluator()
    cb = evaluator.compute_cross_border_analysis()
    assert "cross_border" in cb
    assert "domestic" in cb
    assert cb["cross_border"]["count"] + cb["domestic"]["count"] == 150


def test_evaluator_multi_article_analysis():
    evaluator = T020Evaluator()
    ma = evaluator.compute_multi_article_analysis()
    assert "multi_article" in ma
    assert "single_article" in ma
    assert ma["multi_article"]["count"] + ma["single_article"]["count"] == 150


def test_evaluator_generate_evaluation_reports(tmp_path):
    output_dir = tmp_path / "t020_eval_out"
    evaluator = T020Evaluator()
    jpath, mpath = evaluator.generate_evaluation_reports(output_dir=str(output_dir))

    assert Path(jpath).exists()
    assert Path(mpath).exists()

    with open(jpath, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["evaluation"]["task"] == "T020"
        assert data["summary"]["review_count"] == 150

    with open(mpath, "r", encoding="utf-8") as f:
        content = f.read()
        assert "T020 News Value Evaluation Report" in content
        assert "VERDICT:" in content


def test_evaluator_empty_reviews(tmp_path):
    empty_results = tmp_path / "empty_results.json"
    with open(empty_results, "w", encoding="utf-8") as f:
        json.dump({"reviews": []}, f)

    evaluator = T020Evaluator(review_results_path=str(empty_results))
    st = evaluator.get_review_status()
    assert st["reviewed"] == 0
    assert st["remaining"] == 150
    assert st["completion_rate"] == 0.0
    summary = evaluator.compute_summary_metrics()
    assert summary == {}
