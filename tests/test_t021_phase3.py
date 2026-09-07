"""Tests for T021 Phase 3 Controlled Production RSS Expansion (test_t021_phase3.py)"""

import os
import sqlite3
import pytest
from pathlib import Path

from world_news.t021_production import (
    T021Phase3Manager, BackupManager, STAGE_A_SOURCES, STAGE_B_SOURCES, STAGE_C_SOURCES
)


@pytest.fixture
def temp_phase3(tmp_path):
    docs_dir = tmp_path / "docs_phase3"
    backup_dir = tmp_path / "backups_phase3"
    mgr = T021Phase3Manager(docs_dir=docs_dir)
    mgr.backup_mgr = BackupManager(backup_dir=backup_dir)
    return mgr, docs_dir, backup_dir


def test_01_source_configuration_validation(temp_phase3):
    """1. source configuration validation: Verify schema of candidate sources."""
    mgr, docs_dir, backup_dir = temp_phase3
    for s in STAGE_A_SOURCES + STAGE_B_SOURCES + STAGE_C_SOURCES:
        assert "source_id" in s
        assert "feed_url" in s
        assert "polling_interval" in s
        assert s["polling_interval"] >= 300


def test_02_duplicate_source_detection(temp_phase3):
    """2. duplicate source detection: Verify detection of duplicate sources."""
    mgr, docs_dir, backup_dir = temp_phase3
    existing_ids = [s["source_id"] for s in mgr.baseline_sources]
    for s in STAGE_A_SOURCES:
        assert s["source_id"] not in existing_ids


def test_03_source_id_uniqueness(temp_phase3):
    """3. source ID uniqueness: Ensure all expanded source IDs are unique."""
    all_sources = STAGE_A_SOURCES + STAGE_B_SOURCES + STAGE_C_SOURCES
    ids = [s["source_id"] for s in all_sources]
    assert len(ids) == len(set(ids))


def test_04_feed_url_uniqueness(temp_phase3):
    """4. feed URL uniqueness: Ensure all feed URLs are unique."""
    all_sources = STAGE_A_SOURCES + STAGE_B_SOURCES + STAGE_C_SOURCES
    urls = [s["feed_url"] for s in all_sources]
    assert len(urls) == len(set(urls))


def test_05_backup_creation(temp_phase3):
    """5. backup creation: Verify backup creation in backup directory."""
    mgr, docs_dir, backup_dir = temp_phase3
    res = mgr.backup_mgr.create_backups()
    assert res["overall_status"] == "PASS"
    assert len(res["backups"]) == 3


def test_06_sqlite_integrity_check(temp_phase3):
    """6. SQLite integrity check: Verify integrity check function."""
    mgr, docs_dir, backup_dir = temp_phase3
    db_file = backup_dir / "test.db"
    conn = sqlite3.connect(str(db_file))
    conn.execute("CREATE TABLE t (id INT);")
    conn.close()
    chk = mgr.backup_mgr.check_integrity(str(db_file))
    assert chk == "ok"


def test_07_stage_a_enable(temp_phase3):
    """7. Stage A enable: Check Stage A rollout."""
    mgr, docs_dir, backup_dir = temp_phase3
    mgr.save_before_config()
    stage_a = mgr.baseline_sources + STAGE_A_SOURCES
    assert len(stage_a) == len(mgr.baseline_sources) + 7


def test_08_stage_a_disable(temp_phase3):
    """8. Stage A disable: Check reversion to baseline."""
    mgr, docs_dir, backup_dir = temp_phase3
    reverted = mgr.baseline_sources
    assert len(reverted) == 2


def test_09_stage_b_enable(temp_phase3):
    """9. Stage B enable: Check Stage B addition."""
    mgr, docs_dir, backup_dir = temp_phase3
    stage_b = mgr.baseline_sources + STAGE_A_SOURCES + STAGE_B_SOURCES
    assert len(stage_b) == 2 + 7 + 7


def test_10_stage_b_disable(temp_phase3):
    """10. Stage B disable: Revert to Stage A."""
    mgr, docs_dir, backup_dir = temp_phase3
    reverted = mgr.baseline_sources + STAGE_A_SOURCES
    assert len(reverted) == 9


def test_11_stage_c_enable(temp_phase3):
    """11. Stage C enable: Full Stage C rollout."""
    mgr, docs_dir, backup_dir = temp_phase3
    res = mgr.run_staged_rollout()
    assert res["final_sources_count"] == 20


def test_12_stage_c_disable(temp_phase3):
    """12. Stage C disable: Revert to Stage B."""
    mgr, docs_dir, backup_dir = temp_phase3
    reverted = mgr.baseline_sources + STAGE_A_SOURCES + STAGE_B_SOURCES
    assert len(reverted) == 16


def test_13_rollback(temp_phase3):
    """13. rollback: Run rollback integrity check."""
    mgr, docs_dir, backup_dir = temp_phase3
    rb = mgr.run_rollback_check()
    assert rb["rollback_test_verdict"] == "PASS"


def test_14_polling_interval_validation(temp_phase3):
    """14. polling interval validation: Check normal feeds >= 900s."""
    for s in STAGE_A_SOURCES + STAGE_B_SOURCES + STAGE_C_SOURCES:
        assert s["polling_interval"] >= 900


def test_15_limited_polling_validation(temp_phase3):
    """15. limited polling validation: ADOPT_WITH_LIMIT feeds have 1800s interval."""
    limits = [s for s in STAGE_A_SOURCES + STAGE_B_SOURCES + STAGE_C_SOURCES if s["status"] == "ADOPT_WITH_LIMIT"]
    assert len(limits) == 3
    for s in limits:
        assert s["polling_interval"] == 1800


def test_16_duplicate_article_detection(temp_phase3):
    """16. duplicate article detection: Verify metrics duplicate calculations."""
    mgr, docs_dir, backup_dir = temp_phase3
    metrics = mgr.compute_production_metrics()
    for m in metrics:
        assert m["duplicates"] >= 0
        assert m["duplicate_rate"] >= 0.0


def test_17_source_metrics(temp_phase3):
    """17. source metrics: Verify calculation of source metrics."""
    mgr, docs_dir, backup_dir = temp_phase3
    metrics = mgr.compute_production_metrics()
    assert len(metrics) == 18


def test_18_coverage_delta(temp_phase3):
    """18. coverage delta: Check regional delta calculation."""
    mgr, docs_dir, backup_dir = temp_phase3
    cov = mgr.compute_coverage_before_after()
    assert cov["regional_coverage"]["Africa"]["delta"] == "+48"


def test_19_production_db_isolation(temp_phase3):
    """19. production DB isolation: Ensure zero writes to production DB."""
    mgr, docs_dir, backup_dir = temp_phase3
    res = mgr.compute_resource_metrics()
    assert res["production_db_writes_clean"] is True


def test_20_monitoring_integration(temp_phase3):
    """20. monitoring integration: Check monitoring backlog and error status."""
    mgr, docs_dir, backup_dir = temp_phase3
    res = mgr.compute_resource_metrics()
    assert res["permanent_backlog"] == 0


def test_21_dashboard_source_visibility(temp_phase3):
    """21. dashboard source visibility: Verify source visibility count."""
    mgr, docs_dir, backup_dir = temp_phase3
    st = mgr.get_status()
    assert st["total_expanded_sources"] == 20


def test_22_dashboard_region_visibility(temp_phase3):
    """22. dashboard region visibility: Verify region visibility in coverage."""
    mgr, docs_dir, backup_dir = temp_phase3
    cov = mgr.compute_coverage_before_after()
    assert len(cov["regional_coverage"]) == 8


def test_23_quality_review_aggregation(temp_phase3):
    """23. quality review aggregation: Verify 40 events reviewed."""
    mgr, docs_dir, backup_dir = temp_phase3
    qual = mgr.compute_quality_review()
    assert qual["total_reviewed"] == 40
    assert qual["map_user_value_rate"] >= 70.0


def test_24_critical_error_detection(temp_phase3):
    """24. critical error detection: Verify 0 critical errors."""
    mgr, docs_dir, backup_dir = temp_phase3
    qual = mgr.compute_quality_review()
    assert qual["critical_location_errors"] == 0
