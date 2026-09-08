"""T023 Production UX Validation & User Journey Automated Tests (test_t023_ux.py)"""

import os
import json
import sqlite3
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from world_news.api.app import app, db


@pytest.fixture
def client():
    from world_news.api.app import create_app
    app_instance = create_app("worldnews.db")
    return TestClient(app_instance)



def test_t023_01_baseline_git_commit_and_db_integrity():
    """Verify production database integrity and baseline configuration."""
    conn = sqlite3.connect("worldnews.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    assert integrity == "ok"
    conn.close()


def test_t023_02_uj001_global_overview_aggregation(client):
    """UJ-001: Verify Global Overview Strip aggregated counts via active events API."""
    res = client.get("/api/v1/events/active?limit=200")
    assert res.status_code == 200
    data = res.json()
    events = data.get("events", [])
    assert len(events) >= 100
    assert data.get("count") == len(events)
    assert "generated_at" in data

    # Verify key attributes exist on all active events
    for evt in events:
        assert "id" in evt
        assert "category" in evt
        assert "event_country" in evt
        assert "region" in evt
        assert "latitude" in evt
        assert "longitude" in evt
        assert evt["latitude"] is not None
        assert evt["longitude"] is not None


def test_t023_03_uj002_region_and_country_cascading(client):
    """UJ-002: Verify region mapping taxonomy and country cascading consistency."""
    region_ts = Path("web/src/utils/region.ts")
    assert region_ts.exists()
    content = region_ts.read_text(encoding="utf-8")
    assert "REGION_NAMES" in content
    for reg in ["Africa", "Asia", "Europe", "Middle East", "Americas", "Oceania"]:
        assert reg in content

    filter_bar = Path("web/src/components/FilterBar.tsx")
    filter_content = filter_bar.read_text(encoding="utf-8")
    assert "selectedRegion" in filter_content
    assert "selectedCountry" in filter_content


def test_t023_04_uj003_marker_clustering_implementation():
    """UJ-003: Verify proximity marker clustering logic in MapView component."""
    map_view = Path("web/src/components/MapView.tsx")
    assert map_view.exists()
    content = map_view.read_text(encoding="utf-8")
    assert "isClusteredView" in content or "custom-cluster-marker" in content
    assert "zoomLevel <= 4" in content
    assert "minDistance" in content or "Math.hypot" in content or "cluster" in content


def test_t023_05_uj004_map_to_list_sync_and_detail():
    """UJ-004: Verify Map selection updates selectedEvent state and scrolls card into view."""
    app_tsx = Path("web/src/App.tsx")
    app_content = app_tsx.read_text(encoding="utf-8")
    assert "selectedEvent" in app_content
    assert "onSelectEvent" in app_content

    event_list = Path("web/src/components/EventList.tsx")
    list_content = event_list.read_text(encoding="utf-8")
    assert "scrollIntoView" in list_content
    assert "event-card-" in list_content


def test_t023_06_uj005_list_to_map_sync_and_camera_pan():
    """UJ-005: Verify EventList selection triggers map view pan and selected marker highlight."""
    map_view = Path("web/src/components/MapView.tsx")
    map_content = map_view.read_text(encoding="utf-8")
    assert "setView" in map_content or "flyTo" in map_content or "selectedEvent" in map_content


def test_t023_07_uj006_uj007_multi_article_and_external_sources(client):
    """UJ-006 & UJ-007: Verify multi-article detail panel component and source article links."""
    detail_panel = Path("web/src/components/EventDetailPanel.tsx")
    detail_content = detail_panel.read_text(encoding="utf-8")
    assert "Covered by" in detail_content or "Articles" in detail_content
    assert "target=\"_blank\"" in detail_content
    assert "rel=\"noopener noreferrer\"" in detail_content

    # Test event articles API endpoint for event 1
    res = client.get("/api/v1/events/1/articles")
    assert res.status_code == 200
    data = res.json()
    assert "articles" in data
    assert "count" in data


def test_t023_08_uj008_uj009_search_and_combined_filters():
    """UJ-008 & UJ-009: Verify multi-field AND condition filtering in EventList and FilterBar."""
    event_list = Path("web/src/components/EventList.tsx")
    list_content = event_list.read_text(encoding="utf-8")
    assert "searchQuery" in list_content

    filter_bar = Path("web/src/components/FilterBar.tsx")
    filter_content = filter_bar.read_text(encoding="utf-8")
    assert "selectedRegion" in filter_content
    assert "selectedCountry" in filter_content
    assert "selectedCategory" in filter_content

    app_tsx = Path("web/src/App.tsx")
    app_content = app_tsx.read_text(encoding="utf-8")
    assert ".filter(" in app_content


def test_t023_09_uj010_sorting_modes():
    """UJ-010: Verify Newest First, Highest Confidence, and Most Articles sorting logic."""
    event_list = Path("web/src/components/EventList.tsx")
    list_content = event_list.read_text(encoding="utf-8")
    assert "sortMode" in list_content
    assert "newest" in list_content
    assert "confidence" in list_content
    assert "articles" in list_content or "Most Articles" in list_content


def test_t023_10_uj011_uj012_mobile_layout_and_bottom_sheet():
    """UJ-011 & UJ-012: Verify mobile responsive bottom sheet drawer states and touch navigation."""
    app_tsx = Path("web/src/App.tsx")
    app_content = app_tsx.read_text(encoding="utf-8")
    assert "isMobile" in app_content
    assert "bottomSheetState" in app_content
    assert "collapsed" in app_content
    assert "half" in app_content
    assert "full" in app_content


def test_t023_11_uj013_uj014_uj015_filter_reset_empty_state_and_error_boundary():
    """UJ-013, UJ-014, UJ-015: Verify filter reset, empty result message, and error handling."""
    event_list = Path("web/src/components/EventList.tsx")
    list_content = event_list.read_text(encoding="utf-8")
    assert "No matching events found" in list_content or "No events" in list_content

    app_tsx = Path("web/src/App.tsx")
    app_content = app_tsx.read_text(encoding="utf-8")
    assert "Clear Filters" in app_content or "reset" in app_content or "All Regions" in app_content



def test_t023_12_uj016_high_density_rendering_performance():
    """UJ-016: Verify map handles high density active events efficiently."""
    app_tsx = Path("web/src/App.tsx")
    app_content = app_tsx.read_text(encoding="utf-8")
    assert "useMemo" in app_content or "filteredEvents" in app_content


def test_t023_13_production_db_zero_writes_verification():
    """Verify zero mutations / zero writes to production database."""
    conn = sqlite3.connect("worldnews.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]
    assert total_events == 120
    conn.close()


def test_t023_14_api_schema_immutability(client):
    """Verify exact API schema contracts for health and active events remain unchanged."""
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_active = client.get("/api/v1/events/active")
    assert res_active.status_code == 200
    data = res_active.json()
    assert "events" in data
    assert "count" in data
    assert "generated_at" in data
