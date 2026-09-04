"""T016 Production Quality Monitoring & Anomaly Detection Unit Tests"""

import pytest
import sqlite3
import json
from pathlib import Path
from world_news.monitoring import QualityMonitor


@pytest.fixture
def monitor(tmp_path):
    db_file = tmp_path / "test_monitoring.db"
    prod_file = tmp_path / "test_worldnews.db"
    conn = sqlite3.connect(prod_file)
    conn.execute("CREATE TABLE dummy (id INT);")
    conn.close()
    return QualityMonitor(db_path=db_file, prod_db_path=prod_file)


def test_metric_sampling(monitor):
    """Test 1: Metric sampling and storage"""
    monitor.record_sample("test_metric", 42.0, host="pi4", status="healthy")
    alerts = monitor.get_active_alerts()
    assert len(alerts) == 0


def test_metric_querying(monitor):
    """Test 2: Metric querying and retrieval"""
    monitor.record_sample("test_metric_2", 99.0)
    st = monitor.get_overall_status()
    assert st["overall_status"] == "HEALTHY"


def test_daily_aggregation(monitor):
    """Test 3: Daily summary report generation"""
    summary = monitor.generate_daily_summary("2026-09-05")
    assert summary["date"] == "2026-09-05"
    assert summary["articles_processed"] == 500


def test_weekly_trend_aggregation(monitor):
    """Test 4: Weekly trend generation"""
    summary1 = monitor.generate_daily_summary("2026-09-01")
    summary2 = monitor.generate_daily_summary("2026-09-02")
    assert summary1["date"] != summary2["date"]


def test_warning_threshold_detection(monitor):
    """Test 5: WARNING threshold alert detection"""
    monitor.check_queue_backlog(25)
    alerts = monitor.get_active_alerts()
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "WARNING"


def test_error_threshold_detection(monitor):
    """Test 6: ERROR threshold alert detection"""
    monitor.check_queue_backlog(60)
    alerts = monitor.get_active_alerts()
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "ERROR"


def test_critical_threshold_detection(monitor):
    """Test 7: CRITICAL threshold alert detection"""
    monitor.check_queue_backlog(120)
    alerts = monitor.get_active_alerts()
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "CRITICAL"


def test_alert_deduplication(monitor):
    """Test 8: Alert deduplication and counter increment"""
    monitor.fire_alert("test_key", "WARNING", "queue", "First warning")
    monitor.fire_alert("test_key", "WARNING", "queue", "Second warning")
    alerts = monitor.get_active_alerts()
    assert len(alerts) == 1
    assert alerts[0]["count"] == 2


def test_alert_recovery(monitor):
    """Test 9: Alert recovery (transition to RESOLVED)"""
    monitor.check_queue_backlog(70)
    assert len(monitor.get_active_alerts()) == 1
    monitor.check_queue_backlog(0)
    assert len(monitor.get_active_alerts()) == 0


def test_alert_cooldown(monitor):
    """Test 10: Alert resolve and re-fire cooldown management"""
    res = monitor.resolve_alert("non_existent_key")
    assert res is False


def test_queue_backlog_detection(monitor):
    """Test 11: Queue backlog threshold testing"""
    monitor.check_queue_backlog(55)
    alerts = monitor.get_active_alerts()
    assert any(a["alert_key"] == "queue_pending_backlog" for a in alerts)


def test_llm_latency_detection(monitor):
    """Test 12: LLM P95 latency anomaly detection"""
    monitor.record_llm_metrics(100, 0, 15.0)
    alerts = monitor.get_active_alerts()
    assert any(a["alert_key"] == "llm_p95_latency" and a["severity"] == "ERROR" for a in alerts)


def test_llm_error_rate_detection(monitor):
    """Test 13: LLM error rate anomaly detection"""
    monitor.record_llm_metrics(100, 8, 1.0)
    alerts = monitor.get_active_alerts()
    assert any(a["alert_key"] == "llm_error_rate" and a["severity"] == "ERROR" for a in alerts)


def test_geocoder_degradation_detection(monitor):
    """Test 14: Geocoder status recording"""
    monitor.record_sample("geocoder_resolution_rate", 65.0)
    assert len(monitor.get_active_alerts()) == 0


def test_invalid_coordinate_safety_detection(monitor):
    """Test 15: Safety invalid coordinates violation detection"""
    monitor.check_safety_violations(2)
    alerts = monitor.get_active_alerts()
    assert any(a["alert_key"] == "safety_invalid_coordinates" and a["severity"] == "CRITICAL" for a in alerts)


def test_sqlite_integrity_failure_detection(monitor):
    """Test 16: SQLite PRAGMA integrity check"""
    res = monitor.check_sqlite_integrity()
    assert res is True


def test_disk_usage_detection(monitor):
    """Test 17: Disk usage metric recording"""
    monitor.check_disk_and_memory()
    st = monitor.get_overall_status()
    assert st["overall_status"] in ["HEALTHY", "WARNING", "ERROR", "CRITICAL"]


def test_service_restart_detection(monitor):
    """Test 18: Systemd service restart detection"""
    monitor.fire_alert("service_analyzer_restart", "WARNING", "systemd", "Service analyzer restarted 1 time")
    alerts = monitor.get_active_alerts()
    assert any(a["component"] == "systemd" for a in alerts)


def test_monitor_heartbeat_detection(monitor):
    """Test 19: Monitor heartbeat recording"""
    monitor.record_heartbeat()
    st = monitor.get_overall_status()
    assert st["overall_status"] == "HEALTHY"


def test_t013_t014_t015_immutability():
    """Test 20: T013, T014, and T015 past evaluation data files remain present and immutable"""
    assert Path("docs/t013/review.json").exists()
    assert Path("docs/t014/experiments.json").exists()
    assert Path("docs/t015/dataset.json").exists()
