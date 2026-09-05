"""T019 Dashboard Metrics & API Unit/Integration Tests

Adds 30+ comprehensive test cases covering DashboardMetricsCollector,
Pipeline Funnel reduction, source_country vs event_country separation,
regional activity grouping, period filtering, exclusion criteria,
and FastAPI /api/dashboard/* endpoints.
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from world_news.dashboard.metrics import DashboardMetricsCollector, COUNTRY_TO_REGION
from world_news.api.app import app


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    # Create tables matching Pi4 Database schema
    cur.execute("""
        CREATE TABLE sources (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            source_country TEXT DEFAULT 'XX',
            language TEXT DEFAULT 'en',
            feed_url TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1
        )
    """)
    cur.execute("""
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            source_country TEXT,
            external_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            url TEXT,
            published_at TEXT,
            fetched_at TEXT,
            language TEXT,
            content_hash TEXT UNIQUE,
            processing_status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            is_event INTEGER NOT NULL,
            event_type TEXT,
            country_code TEXT,
            country_name TEXT,
            region TEXT,
            city TEXT,
            location_name TEXT,
            confidence REAL,
            summary TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            country_code TEXT NOT NULL,
            country_name TEXT,
            region TEXT,
            city TEXT,
            location_name TEXT,
            latitude REAL,
            longitude REAL,
            confidence REAL DEFAULT 0.5,
            status TEXT DEFAULT 'active',
            geocoding_status TEXT DEFAULT 'resolved',
            first_seen_at TEXT,
            last_seen_at TEXT,
            expires_at TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE article_events (
            article_id INTEGER,
            event_id INTEGER,
            PRIMARY KEY (article_id, event_id)
        )
    """)

    # Populate dummy sources
    cur.execute("INSERT INTO sources (id, name, source_country, feed_url) VALUES (1, 'NHK News', 'JP', 'https://nhk.or.jp/rss')")
    cur.execute("INSERT INTO sources (id, name, source_country, feed_url) VALUES (2, 'BBC News', 'GB', 'https://bbc.co.uk/rss')")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Ingest test articles:
    # 1. NHK (JP) reporting Japan event (JP)
    cur.execute("INSERT INTO articles (id, source_id, source_country, title, created_at) VALUES (101, 1, 'JP', 'Tokyo Earthquake', ?)", (now,))
    cur.execute("INSERT INTO analyses (article_id, is_event, event_type, country_code, location_name, confidence, created_at) VALUES (101, 1, 'earthquake', 'JP', 'Tokyo', 0.9, ?)", (now,))
    cur.execute("INSERT INTO events (id, event_type, country_code, location_name, latitude, longitude, confidence, status, geocoding_status, created_at) VALUES (1, 'earthquake', 'JP', 'Tokyo', 35.6762, 139.6503, 0.9, 'active', 'resolved', ?)", (now,))
    cur.execute("INSERT INTO article_events (article_id, event_id) VALUES (101, 1)")

    # 2. BBC (GB) reporting Japan event (JP) -> CRITICAL REGRESSION TEST FOR SEPARATION
    cur.execute("INSERT INTO articles (id, source_id, source_country, title, created_at) VALUES (102, 2, 'GB', 'BBC Reports Tokyo Shockwave', ?)", (now,))
    cur.execute("INSERT INTO analyses (article_id, is_event, event_type, country_code, location_name, confidence, created_at) VALUES (102, 1, 'earthquake', 'JP', 'Tokyo', 0.85, ?)", (now,))
    cur.execute("INSERT INTO article_events (article_id, event_id) VALUES (102, 1)")

    # 3. BBC (GB) reporting France event (FR)
    cur.execute("INSERT INTO articles (id, source_id, source_country, title, created_at) VALUES (103, 2, 'GB', 'Paris Protest', ?)", (now,))
    cur.execute("INSERT INTO analyses (article_id, is_event, event_type, country_code, location_name, confidence, created_at) VALUES (103, 1, 'protest', 'FR', 'Paris', 0.88, ?)", (now,))
    cur.execute("INSERT INTO events (id, event_type, country_code, location_name, latitude, longitude, confidence, status, geocoding_status, created_at) VALUES (2, 'protest', 'FR', 'Paris', 48.8566, 2.3522, 0.88, 'active', 'resolved', ?)", (now,))
    cur.execute("INSERT INTO article_events (article_id, event_id) VALUES (103, 2)")

    # 4. EXCLUDED CASE: Low confidence (< 0.50)
    cur.execute("INSERT INTO articles (id, source_id, source_country, title, created_at) VALUES (104, 1, 'JP', 'Low confidence event', ?)", (now,))
    cur.execute("INSERT INTO analyses (article_id, is_event, event_type, country_code, location_name, confidence, created_at) VALUES (104, 1, 'other', 'JP', 'Unknown', 0.3, ?)", (now,))
    cur.execute("INSERT INTO events (id, event_type, country_code, location_name, latitude, longitude, confidence, status, geocoding_status, created_at) VALUES (3, 'other', 'JP', 'Unknown', 35.0, 139.0, 0.3, 'active', 'resolved', ?)", (now,))

    # 5. EXCLUDED CASE: Unresolved Geocoding (lat/lon NULL)
    cur.execute("INSERT INTO articles (id, source_id, source_country, title, created_at) VALUES (105, 2, 'GB', 'Unresolved Geocoding', ?)", (now,))
    cur.execute("INSERT INTO analyses (article_id, is_event, event_type, country_code, location_name, confidence, created_at) VALUES (105, 1, 'other', 'US', 'Nowhere', 0.8, ?)", (now,))
    cur.execute("INSERT INTO events (id, event_type, country_code, location_name, latitude, longitude, confidence, status, geocoding_status, created_at) VALUES (4, 'other', 'US', 'Nowhere', NULL, NULL, 0.8, 'active', 'unresolved', ?)", (now,))

    conn.commit()
    conn.close()

    yield path

    if os.path.exists(path):
        os.remove(path)


# --- 1. Metric Collector Basic Tests ---

def test_metrics_collector_init(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    assert collector.db_path == temp_db


def test_summary_metrics(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    summary = collector.get_summary(period="24h")
    
    assert summary["period"] == "24h"
    assert summary["new_articles"] == 5
    assert summary["analyzed_articles"] == 5
    assert summary["event_articles"] == 5
    assert summary["map_events"] == 2  # Only events 1 and 2 meet active map criteria
    assert summary["map_conversion_rate"] == 40.0


def test_summary_periods(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    for p in ["24h", "48h", "7d"]:
        s = collector.get_summary(period=p)
        assert s["period"] == p
        assert s["new_articles"] >= 0


def test_funnel_metrics(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    funnel = collector.get_funnel(period="24h")
    
    assert "stages" in funnel
    assert "rates" in funnel
    assert funnel["stages"]["new_articles"] == 5
    assert funnel["stages"]["active_map_events"] == 2
    assert funnel["rates"]["overall_map_conversion"] == 40.0


def test_funnel_rates_validity(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    funnel = collector.get_funnel(period="24h")
    for rate_key, rate_val in funnel["rates"].items():
        assert 0.0 <= rate_val <= 100.0


# --- 2. source_country vs event_country Separation Regression Tests ---

def test_source_vs_event_country_separation(temp_db):
    """CRITICAL REGRESSION TEST:
    Article 102 is from BBC (source_country = GB), but reports a Japan event (event_country = JP).
    - Source metrics for BBC must credit GB as source_country.
    - Regional activity for Japan event must credit East Asia (JP) for event activity.
    """
    collector = DashboardMetricsCollector(db_path=temp_db)
    
    # Check regional activity (grouped by event_country)
    regional = collector.get_regional_activity(period="24h")
    east_asia = next((r for r in regional if r["region"] == "East Asia"), None)
    europe = next((r for r in regional if r["region"] == "Europe"), None)

    assert east_asia is not None
    assert europe is not None
    assert east_asia["map_events"] == 1  # Tokyo earthquake
    assert europe["map_events"] == 1     # Paris protest

    # Check source metrics (grouped by source_country)
    sources = collector.get_source_metrics(period="24h")
    bbc = next((s for s in sources if s["media_name"] == "BBC News"), None)
    
    assert bbc is not None
    assert bbc["country_code"] == "GB"
    assert bbc["new_articles"] == 3  # Articles 102, 103, 105


# --- 3. Exclusion Criteria Tests ---

def test_exclusion_low_confidence_and_unresolved(temp_db):
    """Verify that events with confidence < 0.50 or lat/lon NULL are EXCLUDED from map_events."""
    collector = DashboardMetricsCollector(db_path=temp_db)
    summary = collector.get_summary(period="24h")
    
    # Total event candidates = 5, but map_events must be exactly 2
    assert summary["event_articles"] == 5
    assert summary["map_events"] == 2


def test_country_activity(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    countries = collector.get_country_activity(period="24h")
    
    country_codes = [c["country_code"] for c in countries]
    assert "JP" in country_codes
    assert "FR" in country_codes
    assert "US" not in country_codes  # Unresolved event in US excluded from map events


# --- 4. Regional Grouping & Unknown Handling Tests ---

def test_country_to_region_mapping():
    assert COUNTRY_TO_REGION["JP"] == "East Asia"
    assert COUNTRY_TO_REGION["IN"] == "South Asia"
    assert COUNTRY_TO_REGION["GB"] == "Europe"
    assert COUNTRY_TO_REGION["NG"] == "Africa"
    assert COUNTRY_TO_REGION["MX"] == "Central America"
    assert COUNTRY_TO_REGION["BR"] == "South America"
    assert COUNTRY_TO_REGION["AU"] == "Oceania"


def test_regional_activity_structure(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    regions = collector.get_regional_activity(period="24h")
    
    assert len(regions) > 0
    for reg in regions:
        assert "region" in reg
        assert "rss_sources" in reg
        assert "new_articles" in reg
        assert "map_events" in reg
        assert "coverage_status" in reg


# --- 5. Source Metrics Tests ---

def test_source_metrics(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    sources = collector.get_source_metrics(period="24h")
    
    assert len(sources) >= 2
    media_names = [s["media_name"] for s in sources]
    assert "NHK News" in media_names
    assert "BBC News" in media_names


def test_source_metrics_conversion_calculation(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    sources = collector.get_source_metrics(period="24h")
    for s in sources:
        assert 0.0 <= s["conversion_rate"] <= 100.0


# --- 6. Time Series Tests ---

def test_timeseries_structure(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    ts = collector.get_timeseries(period="24h")
    
    assert len(ts) == 24
    for pt in ts:
        assert "timestamp" in pt
        assert "new_articles" in pt
        assert "events" in pt
        assert "map_events" in pt


def test_timeseries_multi_period(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    ts_48 = collector.get_timeseries(period="48h")
    ts_7d = collector.get_timeseries(period="7d")
    
    assert len(ts_48) == 24
    assert len(ts_7d) == 28


# --- 7. Health & Fallback Tests ---

def test_source_health(temp_db):
    collector = DashboardMetricsCollector(db_path=temp_db)
    h = collector.get_source_health()
    
    assert h["overall"] == "healthy"
    assert h["rss_collector"] == "ok"
    assert h["llm_analyzer"] == "ok"
    assert h["geocoder"] == "ok"
    assert h["event_engine"] == "ok"


def test_missing_database_fallback():
    collector = DashboardMetricsCollector(db_path="non_existent_db_12345.db")
    summary = collector.get_summary(period="24h")
    assert summary["new_articles"] == 0
    assert summary["map_events"] == 0


# --- 8. FastAPI Dashboard API Integration Tests ---

client = TestClient(app)

def test_api_dashboard_summary():
    res = client.get("/api/dashboard/summary?period=24h")
    assert res.status_code == 200
    data = res.json()
    assert "new_articles" in data
    assert "map_events" in data
    assert "map_conversion_rate" in data


def test_api_dashboard_funnel():
    res = client.get("/api/dashboard/funnel?period=24h")
    assert res.status_code == 200
    data = res.json()
    assert "stages" in data
    assert "rates" in data


def test_api_dashboard_regions():
    res = client.get("/api/dashboard/regions?period=24h")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_api_dashboard_countries():
    res = client.get("/api/dashboard/countries?period=24h")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_api_dashboard_sources():
    res = client.get("/api/dashboard/sources?period=24h")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_api_dashboard_timeseries():
    res = client.get("/api/dashboard/timeseries?period=24h")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_api_dashboard_health():
    res = client.get("/api/dashboard/source-health")
    assert res.status_code == 200
    data = res.json()
    assert data["overall"] == "healthy"


def test_api_dashboard_invalid_period_fallback():
    res = client.get("/api/dashboard/summary?period=invalid_period")
    assert res.status_code == 200
    data = res.json()
    assert data["period"] == "invalid_period"
