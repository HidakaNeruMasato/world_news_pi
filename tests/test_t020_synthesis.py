"""Unit tests for T020 Synthesis and Recommendations (T020 Phase 4)."""

import os
import json
import pytest
from pathlib import Path
from world_news.quality_evaluator import T020Evaluator


def test_synthesis_json_schema():
    evaluator = T020Evaluator()
    synth = evaluator.compute_synthesis()
    assert "overall_quality" in synth
    assert "problem_separation" in synth
    assert "regional_coverage_analysis" in synth
    assert "source_analysis" in synth
    assert "category_analysis" in synth
    assert "cross_border_findings" in synth
    assert "multi_article_findings" in synth
    assert "potential_missed_events_analysis" in synth
    assert "anomalies" in synth


def test_synthesis_overall_metrics_extraction():
    evaluator = T020Evaluator()
    synth = evaluator.compute_synthesis()
    oq = synth["overall_quality"]
    assert oq["review_count"] == 150
    assert oq["rates"]["map_user_value_rate"] == 84.0
    assert oq["critical_errors"] == 0


def test_synthesis_problem_separation():
    evaluator = T020Evaluator()
    synth = evaluator.compute_synthesis()
    ps = synth["problem_separation"]
    assert ps["content_quality_problem"] is False
    assert ps["coverage_problem"] is True
    assert "Content quality is high" in ps["details"]


def test_regional_priority_classification():
    evaluator = T020Evaluator()
    recs = evaluator.compute_recommendations()
    prio = recs["t021_rss_expansion_priorities"]
    assert "Africa" in prio["priority_a_high"]
    assert "South America" in prio["priority_a_high"]
    assert "Eastern Europe" in prio["priority_a_high"]
    assert "East Asia" in prio["priority_c_low"]


def test_source_priority_classification():
    evaluator = T020Evaluator()
    synth = evaluator.compute_synthesis()
    sa = synth["source_analysis"]
    assert isinstance(sa["high_value_sources"], list)
    assert isinstance(sa["medium_value_sources"], list)
    assert isinstance(sa["low_value_sources"], list)


def test_category_classification():
    evaluator = T020Evaluator()
    synth = evaluator.compute_synthesis()
    ca = synth["category_analysis"]
    assert "earthquake" in ca["high_suitability_categories"]
    assert "wildfire" in ca["high_suitability_categories"]
    assert "economy" in ca["low_suitability_categories"]


def test_decision_matrix_structure():
    evaluator = T020Evaluator()
    recs = evaluator.compute_recommendations()
    matrix = recs["decision_matrix"]
    assert isinstance(matrix, list)
    assert len(matrix) >= 5
    for row in matrix:
        assert "issue" in row
        assert "evidence" in row
        assert "root_cause" in row
        assert "priority" in row
        assert "next_milestone" in row


def test_potential_missed_event_classification():
    evaluator = T020Evaluator()
    synth = evaluator.compute_synthesis()
    missed = synth["potential_missed_events_analysis"]
    assert len(missed) == 3
    classifications = [m["classification"] for m in missed]
    assert "sampling_duplicate" in classifications
    assert "classification_issue" in classifications


def test_duplicate_missed_event_classification():
    evaluator = T020Evaluator()
    synth = evaluator.compute_synthesis()
    missed = synth["potential_missed_events_analysis"]
    dups = [m for m in missed if m["classification"] == "sampling_duplicate"]
    assert len(dups) == 2
    assert dups[0]["event_id"] in [29, 57]


def test_anomaly_reporting():
    evaluator = T020Evaluator()
    synth = evaluator.compute_synthesis()
    anomalies = synth["anomalies"]
    assert "regional_taxonomy_anomaly" in anomalies
    assert "source_country_count_anomaly" in anomalies
    assert anomalies["source_country_count_anomaly"]["reported_count"] == 8
    assert anomalies["source_country_count_anomaly"]["actual_count"] == 15
    assert anomalies["source_country_count_anomaly"]["difference"] == 7


def test_final_verdict():
    evaluator = T020Evaluator()
    recs = evaluator.compute_recommendations()
    assert recs["recommended_next_milestone"] == "T021 Global RSS Coverage Expansion"
    assert recs["final_verdict"] == "PASS"


def test_phase4_report_file_generation(tmp_path):
    output_dir = tmp_path / "t020_phase4_out"
    evaluator = T020Evaluator()
    sj, sm, rj, rm = evaluator.generate_phase4_reports(output_dir=str(output_dir))

    assert Path(sj).exists()
    assert Path(sm).exists()
    assert Path(rj).exists()
    assert Path(rm).exists()

    with open(rm, "r", encoding="utf-8") as f:
        content = f.read()
        assert "# T020 Phase 4 Report" in content
        assert "## 1. Executive Summary" in content
        assert "## 19. Recommended Next Step" in content
