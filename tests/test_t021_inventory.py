"""Unit tests for T021 Global RSS Source Inventory and Coverage Gap Analysis (T021 Phase 1)."""

import os
import json
import pytest
from pathlib import Path
from world_news.quality_evaluator import T021InventoryManager


def test_t021_inventory_summary():
    mgr = T021InventoryManager()
    summary = mgr.get_inventory_summary()
    assert summary["total_candidates"] >= 15
    assert summary["recommended"] >= 10
    assert "Africa" in summary["recommended_by_region"]
    assert "South America" in summary["recommended_by_region"]
    assert "Eastern Europe" in summary["recommended_by_region"]


def test_t021_source_uniqueness():
    mgr = T021InventoryManager()
    ids = [s["source_id"] for s in mgr.candidate_sources]
    urls = [s["feed_url"] for s in mgr.candidate_sources]
    assert len(ids) == len(set(ids)), "Source IDs must be unique"
    assert len(urls) == len(set(urls)), "Feed URLs must be unique"


def test_t021_feed_type_validation():
    mgr = T021InventoryManager()
    for s in mgr.candidate_sources:
        assert s["feed_type"] in ["rss", "atom", "rdf"]


def test_t021_feed_url_validation():
    mgr = T021InventoryManager()
    for s in mgr.candidate_sources:
        assert s["feed_url"].startswith("http://") or s["feed_url"].startswith("https://")


def test_t021_metadata_quality_validation():
    mgr = T021InventoryManager()
    for s in mgr.candidate_sources:
        assert 0 <= s["metadata_quality"] <= 5
        assert 0 <= s["score"] <= 50


def test_t021_candidate_status_validation():
    mgr = T021InventoryManager()
    valid_statuses = ["candidate", "recommended", "needs_review", "rejected", "unavailable", "duplicate"]
    for s in mgr.candidate_sources:
        assert s["status"] in valid_statuses


def test_t021_region_priority_classification():
    mgr = T021InventoryManager()
    matrix = mgr.get_coverage_matrix()
    prio_a = [m["region"] for m in matrix if m["priority"] == "A"]
    assert "Africa" in prio_a
    assert "South America" in prio_a
    assert "Eastern Europe" in prio_a


def test_t021_coverage_gap_matrix_generation():
    mgr = T021InventoryManager()
    matrix = mgr.get_coverage_matrix()
    assert isinstance(matrix, list)
    assert len(matrix) >= 6
    for m in matrix:
        assert "region" in m
        assert "priority" in m
        assert "current_events" in m
        assert "coverage_gap" in m
        assert "candidate_sources" in m


def test_t021_terms_compatibility_validation():
    mgr = T021InventoryManager()
    valid_terms = ["compatible", "review_required", "restricted"]
    for s in mgr.candidate_sources:
        assert s["terms_compatibility"] in valid_terms


def test_t021_file_generation_reports(tmp_path):
    output_dir = tmp_path / "t021_test_out"
    mgr = T021InventoryManager()
    files = mgr.generate_t021_reports(output_dir=str(output_dir))

    assert len(files) == 5
    for fpath in files:
        assert Path(fpath).exists()

    inv_json = output_dir / "source_inventory.json"
    with open(inv_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["inventory"]["task"] == "T021"
        assert len(data["sources"]) >= 15
