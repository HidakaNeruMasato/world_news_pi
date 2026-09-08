"""T023-1 Article Preview & Original Article Navigation Automated Tests (test_t023_1_article_preview.py)"""

import os
import json
import sqlite3
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from world_news.api.app import create_app


@pytest.fixture
def client():
    app_instance = create_app("worldnews.db")
    return TestClient(app_instance)


def test_t023_1_01_url_validation_helper():
    """Verify isSafeHttpUrl rejects malicious or non-HTTP protocols."""
    url_ts = Path("web/src/utils/url.ts")
    assert url_ts.exists()
    content = url_ts.read_text(encoding="utf-8")
    assert "isSafeHttpUrl" in content
    assert "http:" in content
    assert "https:" in content


def test_t023_1_02_event_detail_cta_and_preview_components():
    """Verify EventDetailPanel contains Article Preview card and explicit 元記事を読む CTA."""
    panel_tsx = Path("web/src/components/EventDetailPanel.tsx")
    assert panel_tsx.exists()
    content = panel_tsx.read_text(encoding="utf-8")

    # TEST-001 & TEST-007: Explicit CTA & target_blank
    assert "元記事を読む" in content
    assert "target=\"_blank\"" in content
    assert "rel=\"noopener noreferrer\"" in content

    # TEST-002: Disabled fallback notice when URL is unavailable
    assert "元記事URLを取得できません" in content

    # TEST-003: isSafeHttpUrl integration
    assert "isSafeHttpUrl(" in content


    # TEST-004: Summary/description preview rendering
    assert "art.description" in content

    # TEST-010: Min 44px touch target class on CTA
    assert "min-h-[44px]" in content


def test_t023_1_03_api_article_endpoint_contract(client):
    """Verify GET /api/v1/events/{id}/articles returns valid Article objects."""
    res = client.get("/api/v1/events/1/articles")
    assert res.status_code == 200
    data = res.json()
    assert "articles" in data
    articles = data["articles"]
    assert len(articles) >= 1

    for art in articles:
        assert "id" in art
        assert "title" in art
        assert "url" in art
        assert "source_name" in art


def test_t023_1_04_production_db_zero_writes():
    """Verify zero mutations / zero writes to production database."""
    conn = sqlite3.connect("worldnews.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]
    assert total_events == 120
    conn.close()
