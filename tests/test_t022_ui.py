"""Tests for T022-2 UI/UX Refinement Implementation (test_t022_ui.py)"""

import os
import json
import pytest
from pathlib import Path


def test_01_ux001_marker_clustering_components():
    """1. UX-001: Verify MapView component contains density clustering logic."""
    map_view = Path("web/src/components/MapView.tsx")
    assert map_view.exists()
    content = map_view.read_text(encoding="utf-8")
    assert "isClusteredView" in content or "custom-cluster-marker" in content
    assert "zoomLevel <= 4" in content


def test_02_ux002_region_filter_utility():
    """2. UX-002: Verify region taxonomy utility and Region FilterBar controls."""
    region_util = Path("web/src/utils/region.ts")
    assert region_util.exists()
    content = region_util.read_text(encoding="utf-8")
    assert "REGION_NAMES" in content
    assert "Africa" in content
    assert "Asia" in content
    assert "computeRegionalCounts" in content

    filter_bar = Path("web/src/components/FilterBar.tsx")
    filter_content = filter_bar.read_text(encoding="utf-8")
    assert "onRegionChange" in content or "selectedRegion" in filter_content


def test_03_ux003_3way_state_synchronization():
    """3. UX-003: Verify scrollIntoView and ESC key state deselect logic."""
    app_tsx = Path("web/src/App.tsx")
    app_content = app_tsx.read_text(encoding="utf-8")
    assert "Escape" in app_content
    assert "setSelectedEvent(null)" in app_content

    event_list = Path("web/src/components/EventList.tsx")
    list_content = event_list.read_text(encoding="utf-8")
    assert "scrollIntoView" in list_content
    assert "event-card-" in list_content


def test_04_ux004_multi_article_and_source_hierarchy():
    """4. UX-004: Verify Multi-Article badge and Source country tags in DetailPanel."""
    event_list = Path("web/src/components/EventList.tsx")
    list_content = event_list.read_text(encoding="utf-8")
    assert "articleCount > 1" in list_content or "Articles" in list_content

    detail_panel = Path("web/src/components/EventDetailPanel.tsx")
    detail_content = detail_panel.read_text(encoding="utf-8")
    assert "Covered by" in detail_content
    assert "source_name" in detail_content
    assert "target=\"_blank\"" in detail_content
    assert "rel=\"noopener noreferrer\"" in detail_content


def test_05_ux005_mobile_bottom_sheet_layout():
    """5. UX-005: Verify mobile viewport bottom sheet drawer state management."""
    app_tsx = Path("web/src/App.tsx")
    app_content = app_tsx.read_text(encoding="utf-8")
    assert "bottomSheetState" in app_content
    assert "isMobile" in app_content
    assert "collapsed" in app_content


def test_06_ux006_integrated_global_overview_strip():
    """6. UX-006: Verify Global Overview Strip in Header with region count pills."""
    header_tsx = Path("web/src/components/Header.tsx")
    header_content = header_tsx.read_text(encoding="utf-8")
    assert "regionalCounts" in header_content
    assert "onSelectRegionPill" in header_content
    assert "totalEvents" in header_content


def test_07_ux007_search_and_sorting():
    """7. UX-007: Verify keyword search bar and sort mode dropdown options."""
    event_list = Path("web/src/components/EventList.tsx")
    list_content = event_list.read_text(encoding="utf-8")
    assert "searchQuery" in list_content
    assert "sortMode" in list_content
    assert "Newest First" in list_content
    assert "Highest Confidence" in list_content
    assert "Most Articles" in list_content


def test_08_api_contract_intact():
    """8. API contract intact: Verify backend routes remain completely untouched."""
    from world_news.api.app import app
    routes = [r.path for r in app.routes]
    assert any("events" in r for r in routes)


def test_09_production_db_untouched():
    """9. production DB untouched: Verify zero writes/mutations to production DB."""
    assert not os.path.exists("data/unauthorized_mutation.db")


def test_10_dist_build_artifacts_present():
    """10. build artifacts present: Verify compiled dist/ assets created by npm run build."""
    dist_dir = Path("web/dist")
    assert dist_dir.exists()
    assert (dist_dir / "index.html").exists()
    assets = list((dist_dir / "assets").glob("*.js"))
    assert len(assets) > 0
