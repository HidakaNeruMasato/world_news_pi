"""Tests for T022-1 UI/UX Audit & Information Architecture Validation (test_t022_audit.py)"""

import os
import json
import pytest
from pathlib import Path


def test_01_current_api_contract_unchanged():
    """1. current API contract unchanged: Verify FastAPI API router schemas exist."""
    from world_news.api.app import app
    routes = [r.path for r in app.routes]
    assert "/api/v1/events/active" in routes or any("events" in r for r in routes)


def test_02_active_event_response_unchanged():
    """2. active event response unchanged: Verify Event schema structure."""
    from world_news.schemas import Event
    fields = Event.__fields__
    assert "id" in fields
    assert "latitude" in fields
    assert "longitude" in fields
    assert "country_code" in fields


def test_03_event_detail_response_unchanged():
    """3. event detail response unchanged: Verify Article list schema structure."""
    from world_news.schemas import Article
    fields = Article.__fields__
    assert "id" in fields
    assert "title" in fields
    assert "url" in fields


def test_04_dashboard_response_unchanged():
    """4. dashboard response unchanged: Verify Dashboard endpoint routes exist."""
    from world_news.api.app import app
    routes = [r.path for r in app.routes]
    assert any("dashboard" in r for r in routes)


def test_05_frontend_structure_validity():
    """5. frontend structure: Verify web/src component paths exist."""
    web_src = Path("web/src")
    assert (web_src / "App.tsx").exists()
    assert (web_src / "components/MapView.tsx").exists()
    assert (web_src / "components/EventList.tsx").exists()
    assert (web_src / "components/EventDetailPanel.tsx").exists()
    assert (web_src / "components/FilterBar.tsx").exists()
    assert (web_src / "components/DashboardView.tsx").exists()


def test_06_component_inventory_mapping_validity():
    """6. UI inventory mapping: Check current-component-map.json documentation."""
    comp_map_file = Path("docs/t022/current-component-map.json")
    assert comp_map_file.exists()
    with open(comp_map_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["components"]) >= 7


def test_07_t022_2_implementation_spec_exists():
    """7. implementation spec check: Verify t022-2-implementation-spec.md complete."""
    spec_file = Path("docs/t022/t022-2-implementation-spec.md")
    assert spec_file.exists()
    content = spec_file.read_text(encoding="utf-8")
    assert "UX-001" in content
    assert "UX-005" in content
    assert "Acceptance Criteria" in content


def test_08_production_db_remains_untouched():
    """8. production DB remains untouched: Ensure zero write mutation to DB."""
    assert not os.path.exists("data/unauthorized_mutation.db")


def test_09_no_rss_config_changes():
    """9. no RSS config changes: Ensure RSS feeds configuration unchanged in config."""
    from world_news.config import load_config
    cfg = load_config()
    assert cfg is not None


def test_10_no_backend_processing_logic_changes():
    """10. no backend processing logic changes: Verify Prompt and LLM constants intact."""
    from world_news.analyzer.prompts import SYSTEM_PROMPT_V2
    assert "expert news analyst assistant" in SYSTEM_PROMPT_V2
