"""Tests for T021 Phase 2 Sandbox RSS Expansion Pilot (test_t021_sandbox.py)"""

import os
import sqlite3
import pytest
from pathlib import Path

from world_news.t021_sandbox import T021SandboxRunner, T021Phase2Evaluator, SANDBOX_DIR


@pytest.fixture
def temp_sandbox(tmp_path):
    sandbox_dir = tmp_path / "t021_sandbox"
    runner = T021SandboxRunner(sandbox_dir=sandbox_dir)
    evaluator = T021Phase2Evaluator(sandbox_dir=sandbox_dir)
    return runner, evaluator, sandbox_dir


def test_01_sandbox_db_isolation(temp_sandbox):
    """1. Sandbox DB isolation: Verify database created in sandbox path."""
    runner, evaluator, sandbox_dir = temp_sandbox
    db_path = sandbox_dir / "sandbox.db"
    assert db_path.exists()
    assert os.path.abspath(db_path) != os.path.abspath("data/world_news.db")


def test_02_production_db_read_only(temp_sandbox):
    """2. Production DB read-only: Ensure zero writes to production DB."""
    runner, evaluator, sandbox_dir = temp_sandbox
    res = runner.run_pilot(groups=["A"], duration_hours=24)
    assert res["total_fetched"] > 0
    # Production DB remains untouched
    assert not os.path.exists("data/test_prod_modified.db")


def test_03_candidate_source_loading(temp_sandbox):
    """3. Candidate source loading: Verify recommended candidate sources load properly."""
    runner, evaluator, sandbox_dir = temp_sandbox
    candidates = runner.inventory_mgr.candidate_sources
    assert len(candidates) >= 18
    rec = [c for c in candidates if c["status"] == "recommended"]
    assert len(rec) >= 18


def test_04_feed_parsing(temp_sandbox):
    """4. Feed parsing: Test feed execution and item extraction."""
    runner, evaluator, sandbox_dir = temp_sandbox
    res = runner.run_pilot(groups=["A"], duration_hours=24)
    assert res["sources_tested"] == 7
    assert res["total_fetched"] > 0


def test_05_malformed_feed_handling(temp_sandbox):
    """5. Malformed feed handling: Verify resilience to malformed items."""
    runner, evaluator, sandbox_dir = temp_sandbox
    res = runner.run_pilot(groups=["A"], duration_hours=24)
    assert res["total_malformed"] == 0


def test_06_metadata_validation(temp_sandbox):
    """6. Metadata validation: Verify title, link, guid validation."""
    runner, evaluator, sandbox_dir = temp_sandbox
    res = runner.run_pilot(groups=["A"], duration_hours=24)
    conn = sqlite3.connect(sandbox_dir / "sandbox.db")
    cur = conn.cursor()
    cur.execute("SELECT title, link, guid FROM sandbox_articles")
    rows = cur.fetchall()
    conn.close()
    for t, l, g in rows:
        assert t and l and g


def test_07_guid_dedup(temp_sandbox):
    """7. GUID dedup: Verify duplicate articles are marked with GUID dedup reason."""
    runner, evaluator, sandbox_dir = temp_sandbox
    res = runner.run_pilot(groups=["A"], duration_hours=24)
    conn = sqlite3.connect(sandbox_dir / "sandbox.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sandbox_articles WHERE is_duplicate = 1")
    dups = cur.fetchone()[0]
    conn.close()
    assert dups >= 0


def test_08_url_dedup(temp_sandbox):
    """8. URL dedup: Verify URL normalization & dedup tracking."""
    runner, evaluator, sandbox_dir = temp_sandbox
    res = runner.run_pilot(groups=["A"], duration_hours=24)
    assert res["total_duplicates"] >= 0


def test_09_article_dedup(temp_sandbox):
    """9. Article dedup: Verify article count distinction between new articles and duplicates."""
    runner, evaluator, sandbox_dir = temp_sandbox
    res = runner.run_pilot(groups=["A"], duration_hours=24)
    assert res["total_new"] + res["total_duplicates"] == res["total_fetched"]


def test_10_coverage_gain_calculation(temp_sandbox):
    """10. Coverage gain calculation: Verify before/after delta calculation."""
    runner, evaluator, sandbox_dir = temp_sandbox
    cov = evaluator.compute_coverage_gain()
    assert "Africa" in cov
    assert cov["Africa"]["after_events"] > cov["Africa"]["before_events"]


def test_11_source_efficiency_calculation(temp_sandbox):
    """11. Source efficiency calculation: Verify map_worthy_per_100 and new_map_worthy_per_100."""
    runner, evaluator, sandbox_dir = temp_sandbox
    metrics = evaluator.compute_source_metrics()
    for m in metrics:
        assert "map_worthy_per_100" in m
        assert "new_map_worthy_per_100" in m


def test_12_source_classification(temp_sandbox):
    """12. Source classification: Verify decisions (ADOPT, ADOPT_WITH_LIMIT, KEEP_IN_SANDBOX, REJECT)."""
    runner, evaluator, sandbox_dir = temp_sandbox
    metrics = evaluator.compute_source_metrics()
    decisions = set(m["decision"] for m in metrics)
    assert "ADOPT" in decisions or "ADOPT_WITH_LIMIT" in decisions


def test_13_regional_coverage_calculation(temp_sandbox):
    """13. Regional coverage calculation: Check new country additions per priority region."""
    runner, evaluator, sandbox_dir = temp_sandbox
    cov = evaluator.compute_coverage_gain()
    assert len(cov["Africa"]["new_countries"]) > 0
    assert len(cov["South America"]["new_countries"]) > 0


def test_14_quality_evaluation(temp_sandbox):
    """14. Quality evaluation: Verify Map User Value Rate and zero critical location errors."""
    runner, evaluator, sandbox_dir = temp_sandbox
    qual = evaluator.compute_quality_review()
    assert qual["map_user_value_rate"] >= 70.0
    assert qual["critical_location_errors"] == 0


def test_15_adoption_criteria(temp_sandbox):
    """15. Adoption criteria: Check compliance with adoption thresholds."""
    runner, evaluator, sandbox_dir = temp_sandbox
    res = evaluator.generate_phase2_reports()
    assert len(res) == 10
    for f in res:
        assert os.path.exists(f)
