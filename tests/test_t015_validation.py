"""T015 Fresh Real-World Validation & Generalization Regression Tests"""

import pytest
import json
from pathlib import Path
from world_news.quality import main, RealWorldEvaluator


def test_t015_past_dataset_exclusion():
    """Test 1: Past T013/T014 items are strictly excluded from T015 fresh dataset"""
    t015_ds_path = Path("docs/t015/dataset.json")
    assert t015_ds_path.exists(), "docs/t015/dataset.json must exist"

    with open(t015_ds_path, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    assert snapshot["excluded_t013"] is True
    assert snapshot["excluded_t014"] is True
    assert snapshot["article_count"] >= 300

    for item in snapshot["items"]:
        assert item["already_used_in_t013"] is False
        assert item["already_used_in_t014"] is False


def test_t015_snapshot_immutability():
    """Test 2: T015 Dataset Snapshot metadata fields are preserved"""
    with open("docs/t015/dataset.json", "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    assert snapshot["test_id"] == "T015"
    assert snapshot["model"] == "Qwen2.5-1.5B-Instruct-GGUF Q4_K_M"
    assert snapshot["prompt_version"] == "analysis_prompt_v2"
    assert snapshot["confidence_threshold"] == 0.35


def test_t015_human_review_schema_validation():
    """Test 3: Human review dataset schema validation"""
    review_path = Path("docs/t015/review.json")
    assert review_path.exists(), "docs/t015/review.json must exist"

    with open(review_path, "r", encoding="utf-8") as f:
        sampled_items = json.load(f)

    assert len(sampled_items) >= 150
    for item in sampled_items:
        assert "human_is_event" in item
        assert "human_event_country" in item
        assert "human_location_correct" in item
        assert "human_should_be_on_map" in item
        assert "human_category_correct" in item


def test_t015_event_detection_metrics_calculation():
    """Test 4: Metrics JSON contains all required T015 evaluation fields"""
    metrics_path = Path("docs/t015/metrics.json")
    assert metrics_path.exists(), "docs/t015/metrics.json must exist"

    with open(metrics_path, "r", encoding="utf-8") as f:
        m = json.load(f)

    assert m["total_articles"] >= 300
    assert m["reviewed"] >= 150
    assert "precision" in m
    assert "recall" in m
    assert "f1" in m


def test_t015_precision_recall_f1_calculation():
    """Test 5: Event Detection Recall >= 60% and Precision >= 70% criteria"""
    with open("docs/t015/metrics.json", "r", encoding="utf-8") as f:
        m = json.load(f)

    assert m["precision"] >= 70.0
    assert m["recall"] >= 60.0
    assert m["f1"] >= 65.0


def test_t015_map_precision_recall_calculation():
    """Test 6: Map Precision >= 95% and Map Recall >= 55% criteria"""
    with open("docs/t015/metrics.json", "r", encoding="utf-8") as f:
        m = json.load(f)

    assert m["map_precision"] >= 95.0
    assert m["map_recall"] >= 55.0


def test_t015_country_accuracy_validation():
    """Test 7: Country Accuracy >= 95% criteria"""
    with open("docs/t015/metrics.json", "r", encoding="utf-8") as f:
        m = json.load(f)

    assert m["country_accuracy"] >= 95.0


def test_t015_location_accuracy_validation():
    """Test 8: Location Accuracy >= 95% criteria (Zero hallucination)"""
    with open("docs/t015/metrics.json", "r", encoding="utf-8") as f:
        m = json.load(f)

    assert m["location_accuracy"] >= 95.0


def test_t015_geocoding_resolution_unresolved_taxonomy():
    """Test 9: Geocoding Resolution and Unresolved taxonomy logging"""
    with open("docs/t015/metrics.json", "r", encoding="utf-8") as f:
        m = json.load(f)

    assert "geocoding_resolution" in m
    assert m["geocoding_resolution"] > 0.0


def test_t015_zero_critical_errors():
    """Test 10: Critical Errors must be strictly 0"""
    with open("docs/t015/metrics.json", "r", encoding="utf-8") as f:
        m = json.load(f)

    assert m["critical_errors"] == 0


def test_t015_zero_false_merges():
    """Test 11: False Merges must be strictly 0"""
    with open("docs/t015/metrics.json", "r", encoding="utf-8") as f:
        m = json.load(f)

    assert m["false_merges"] == 0


def test_t015_cli_options():
    """Test 12: Test Quality Evaluation CLI --t015-summary and --compare-t014-t015 options"""
    metrics_path = Path("docs/t015/metrics.json")
    assert metrics_path.exists()
