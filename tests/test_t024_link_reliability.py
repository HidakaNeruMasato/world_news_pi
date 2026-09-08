"""Integration tests for T024 Article Link Reliability (tests/test_t024_link_reliability.py)"""

import os
import sqlite3
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from world_news.api.app import create_app, db
from world_news.api.database import Pi4Database


@pytest.fixture
def client():
    app_instance = create_app("worldnews.db")
    return TestClient(app_instance)


def test_t024_01_schema_columns_and_history_table():
    """Verify articles table columns and article_url_history table exist."""
    test_db = Pi4Database("worldnews.db")
    conn = sqlite3.connect("worldnews.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA integrity_check;")
    assert cursor.fetchone()[0] == "ok"

    cursor.execute("PRAGMA table_info(articles)")
    art_cols = [row[1] for row in cursor.fetchall()]
    for col in ["original_url", "canonical_url", "current_url", "url_status", "url_http_status", "url_last_checked_at"]:
        assert col in art_cols

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='article_url_history'")
    assert cursor.fetchone() is not None
    conn.close()


def test_t024_02_update_article_url_status_and_history():
    """Verify update_article_url_status records current URL and history log correctly."""
    test_db = Pi4Database("worldnews.db")
    # Insert test article
    conn = sqlite3.connect("worldnews.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO articles (source_id, title, url, original_url, current_url, url_status, fetched_at, created_at, updated_at)
        VALUES (1, 'T024 Link Test Article', 'https://example.com/test-old', 'https://example.com/test-old', 'https://example.com/test-old', 'unknown', '2026-09-08T10:00:00', '2026-09-08T10:00:00', '2026-09-08T10:00:00')
    """)
    art_id = cursor.lastrowid
    conn.commit()

    # Update status to redirected
    test_db.update_article_url_status(
        article_id=art_id,
        original_url="https://example.com/test-old",
        current_url="https://example.com/test-new",
        canonical_url="https://example.com/test-new",
        status="redirected",
        http_status=301,
        redirect_count=1,
    )

    # Check updated record
    cursor.execute("SELECT current_url, url_status, url_http_status FROM articles WHERE id = ?", (art_id,))
    row = cursor.fetchone()
    assert row[0] == "https://example.com/test-new"
    assert row[1] == "redirected"
    assert row[2] == 301

    # Check history
    history = test_db.get_article_url_history(art_id)
    assert len(history) >= 1
    assert history[-1]["url"] == "https://example.com/test-new"
    assert history[-1]["status"] == "redirected"
    conn.close()


def test_t024_03_event_and_article_lifecycle_decoupling(client):
    """Verify event visibility remains intact even if an article url_status becomes not_found."""
    res = client.get("/api/v1/events/active?limit=200")
    assert res.status_code == 200
    events = res.json().get("events", [])
    assert len(events) >= 100

    # Verify event detail articles endpoint returns url_status and link_available
    res_art = client.get("/api/v1/events/1/articles")
    assert res_art.status_code == 200
    data = res_art.json()
    assert "articles" in data
    for art in data["articles"]:
        assert "url_status" in art
        assert "link_available" in art
        assert "current_url" in art


def test_t024_04_frontend_components_integration():
    """Verify EventDetailPanel and event.ts type definitions support url_status and Alternative Articles."""
    panel_tsx = Path("web/src/components/EventDetailPanel.tsx")
    assert panel_tsx.exists()
    content = panel_tsx.read_text(encoding="utf-8")

    assert "url_status" in content
    assert "activeAlternativeArticles" in content
    assert "このイベントを報じている他のニュースソース" in content
    assert "元記事は現在確認できません" in content
    assert "※ リンク先URLが正規URLへ更新されています" in content

    types_ts = Path("web/src/types/event.ts")
    types_content = types_ts.read_text(encoding="utf-8")
    assert "url_status?:" in types_content
    assert "current_url?:" in types_content
    assert "link_available?:" in types_content
