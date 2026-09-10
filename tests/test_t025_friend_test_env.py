"""T025 外部ユーザーテスト環境 Security & Isolation 自動検証テスト

テスト項目:
1. worldnews_test.db スナップショット自動生成とメタデータ検証
2. Friend Test API 公開 GET エンドポイント動作検証 (/api/health, /api/events/active, /api/events/{id}/articles, /api/v1/events/{id}/reachability)
3. 書き込み系 API (POST, PUT, DELETE) 遮断検証 (405/403)
4. 内部 API / 管理機能 (internal, dashboard, stats, admin) 遮断検証 (403)
5. Rate Limiting 制御検証 (60 req/min 超過時に 429)
6. CORS 制限検証
7. 本番 DB 非侵襲検証 (worldnews.db への非侵襲)
"""

import os
import gc
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from scripts.t025_create_test_db import create_test_db_snapshot
from world_news.api.friend_api import create_friend_app
from world_news.api.database import Pi4Database


@pytest.fixture
def test_dbs():
    """本番 DB ダミーとテスト DB のテンポラリ作成フィクスチャ"""
    with tempfile.NamedTemporaryFile(suffix="_prod.db", delete=False) as f_prod:
        prod_path = Path(f_prod.name)
    with tempfile.NamedTemporaryFile(suffix="_test.db", delete=False) as f_test:
        test_path = Path(f_test.name)

    # 本番 DB 初期化
    prod_db = Pi4Database(db_path=str(prod_path))
    
    # ダミーイベント & 記事データの挿入
    now_str = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(str(prod_path)) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events (event_type, country_code, latitude, longitude, confidence, status, geocoding_status, first_seen_at, last_seen_at, created_at, updated_at)
            VALUES ('security_test', 'JP', 35.6762, 139.6503, 0.95, 'active', 'resolved', ?, ?, ?, ?)
        """, (now_str, now_str, now_str, now_str))
        event_id = cur.lastrowid

        cur.execute("""
            INSERT INTO articles (source_id, title, url, original_url, current_url, url_status, event_id, fetched_at, created_at, updated_at)
            VALUES (1, 'T025 Security Test Article', 'https://example.com/t025-test', 'https://example.com/t025-test', 'https://example.com/t025-test', 'active', ?, ?, ?, ?)
        """, (event_id, now_str, now_str, now_str))
        conn.commit()

    # スナップショット生成
    create_test_db_snapshot(prod_db=str(prod_path), test_db=str(test_path))

    yield str(prod_path), str(test_path)

    gc.collect()
    for p in (prod_path, test_path):
        if p.exists():
            try:
                p.unlink()
            except PermissionError:
                pass


@pytest.fixture
def friend_client(test_dbs):
    """Friend Test Client フィクスチャ"""
    prod_path, test_path = test_dbs
    app = create_friend_app(db_path=test_path)
    client = TestClient(app)
    return client, prod_path, test_path


# 1. Test DB Snapshot & Metadata
def test_t025_snapshot_generation(test_dbs):
    prod_path, test_path = test_dbs

    assert os.path.exists(test_path)
    conn = sqlite3.connect(test_path)
    cur = conn.cursor()

    cur.execute("SELECT key, value FROM test_db_metadata;")
    meta = dict(cur.fetchall())
    conn.close()

    assert meta.get("environment") == "friend_test_readonly"
    assert "snapshot_timestamp" in meta
    assert int(meta.get("event_count", 0)) >= 1
    assert int(meta.get("article_count", 0)) >= 1


# 2. Public GET Endpoints
def test_t025_public_get_endpoints(friend_client):
    client, _, _ = friend_client

    # Health check
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    assert res_health.json()["environment"] == "friend_test_readonly"

    # Active events
    res_events = client.get("/api/events/active")
    assert res_events.status_code == 200
    data = res_events.json()
    assert "events" in data
    assert data["count"] >= 1
    event_id = data["events"][0]["id"]

    # Articles by event ID
    res_articles = client.get(f"/api/events/{event_id}/articles")
    assert res_articles.status_code == 200
    assert "articles" in res_articles.json()

    # Reachability by event ID
    res_reachability = client.get(f"/api/v1/events/{event_id}/reachability")
    assert res_reachability.status_code == 200


# 3. Write Method Blocking (POST, PUT, DELETE -> 405)
def test_t025_write_methods_blocked(friend_client):
    client, _, _ = friend_client

    res_post = client.post("/api/events/active", json={"data": "test"})
    assert res_post.status_code in (405, 403)

    res_put = client.put("/api/events/1", json={"data": "test"})
    assert res_put.status_code in (405, 403)

    res_delete = client.delete("/api/events/1")
    assert res_delete.status_code in (405, 403)


# 4. Internal API Blocking (/api/v1/internal/*, /api/dashboard/*, etc. -> 403)
def test_t025_internal_endpoints_blocked(friend_client):
    client, _, _ = friend_client

    internal_paths = [
        "/api/v1/internal/articles",
        "/api/v1/internal/jobs",
        "/api/dashboard/summary",
        "/api/v1/events/stats",
        "/admin/settings",
        "/api/v1/link-check",
    ]
    for path in internal_paths:
        res = client.get(path)
        assert res.status_code == 403
        assert "Access Denied" in res.json().get("detail", "")


# 5. Rate Limiting Verification (超過時 429)
def test_t025_rate_limiting(friend_client):
    client, _, _ = friend_client

    # 60 回呼び出し (制限内)
    for _ in range(60):
        res = client.get("/api/v1/health")
        assert res.status_code == 200

    # 61 回目 (超過)
    res_over = client.get("/api/v1/health")
    assert res_over.status_code == 429
    assert "Too Many Requests" in res_over.json().get("detail", "")


# 6. CORS Handling
def test_t025_cors_headers(friend_client):
    client, _, _ = friend_client

    headers = {"Origin": "https://friend.github.io"}
    res = client.get("/api/v1/health", headers=headers)
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "https://friend.github.io"


# 7. Production Database Non-Invasion
def test_t025_prod_db_non_invasion(friend_client):
    client, prod_path, _ = friend_client

    # 本番 DB の mtime および データ件数記録
    conn_before = sqlite3.connect(prod_path)
    cur_before = conn_before.cursor()
    cur_before.execute("SELECT COUNT(*) FROM articles;")
    art_count_before = cur_before.fetchone()[0]
    conn_before.close()

    # Friend API に対して操作を実行
    client.get("/api/events/active")

    # 本番 DB のデータ件数が変動していないことを確認
    conn_after = sqlite3.connect(prod_path)
    cur_after = conn_after.cursor()
    cur_after.execute("SELECT COUNT(*) FROM articles;")
    art_count_after = cur_after.fetchone()[0]
    conn_after.close()

    assert art_count_before == art_count_after
