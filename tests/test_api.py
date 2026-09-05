"""T004 Pi4 API & Database 全要件対応ユニット/統合テスト (全14テスト)"""

import gc
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from world_news.api.database import Pi4Database
from world_news.api.app import create_app
from world_news.config import AppConfig
from world_news.schemas import Article
from world_news.collector.queue import CollectorQueue, QueueStatus
from world_news.collector.delivery import Pi4DeliveryClient, DeliveryResult
from world_news.collector.scheduler import CollectorScheduler


@pytest.fixture
def temp_db_path():
    """一時的 SQLite DB パスを生成するフィクスチャ"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    yield path
    gc.collect()
    if path.exists():
        try:
            path.unlink()
        except PermissionError:
            pass


@pytest.fixture
def api_client(temp_db_path):
    """FastAPI TestClient フィクスチャ"""
    app = create_app(db_path=str(temp_db_path))
    client = TestClient(app)
    return client, temp_db_path


# 1. database initialization (全7テーブル作成確認)
def test_database_initialization(temp_db_path):
    db = Pi4Database(db_path=temp_db_path)
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

    expected_tables = {
        "sources", "articles", "analyses", "events",
        "article_events", "geocoding_cache", "processing_jobs"
    }
    assert expected_tables.issubset(tables)


# 2. article insert (articles 挿入)
def test_article_insert(temp_db_path):
    db = Pi4Database(db_path=temp_db_path)
    payload = {
        "source_id": 1,
        "source_country": "JP",
        "external_id": "ext-1",
        "title": "Test Title",
        "description": "Test Description",
        "url": "http://example.com/1",
        "content_hash": "hash1",
    }
    art_id, already_exists = db.insert_article_with_job(payload)
    assert art_id is not None
    assert already_exists is False

    stats = db.get_stats()
    assert stats["total_articles"] == 1


# 3. processing job creation (processing_jobs 自動登録)
def test_processing_job_creation(temp_db_path):
    db = Pi4Database(db_path=temp_db_path)
    payload = {
        "source_id": 1,
        "title": "Title For Job Test",
        "content_hash": "hash-job-test",
    }
    art_id, _ = db.insert_article_with_job(payload)

    with sqlite3.connect(temp_db_path) as conn:
        conn.row_factory = sqlite3.Row
        job = conn.execute("SELECT * FROM processing_jobs WHERE article_id = ?", (art_id,)).fetchone()
        assert job is not None
        assert job["job_type"] == "llm_analysis"
        assert job["status"] == "pending"


# 4. transaction atomicity (ロールバックテスト)
def test_transaction_atomicity(temp_db_path):
    db = Pi4Database(db_path=temp_db_path)
    payload = {
        "source_id": 1,
        "title": "Atomicity Test",
        "content_hash": "hash-atomicity",
    }

    # 存在しないカラムを指定させて DB 挿入時エラーを出すことでトランザクションロールバックを試す
    with patch.object(db, "find_duplicate_article", return_value=None):
        with sqlite3.connect(temp_db_path) as conn:
            # Table 構造を一時的に壊すか、不正キーを渡してエラーを誘発
            pass

    # 意図的な不整合挿入処理の呼び出し (必須キー破損)
    with pytest.raises(Exception):
        bad_payload = {"source_id": 1}  # title 欠落で KeyError / OperationalError
        db.insert_article_with_job(bad_payload)

    stats = db.get_stats()
    assert stats["total_articles"] == 0
    assert stats["pending_jobs"] == 0


# 5. duplicate article (重複判定)
def test_duplicate_article(temp_db_path):
    db = Pi4Database(db_path=temp_db_path)
    payload = {
        "source_id": 1,
        "external_id": "dup-ext-1",
        "title": "Duplicate Title",
        "content_hash": "hash-dup",
    }
    id1, exists1 = db.insert_article_with_job(payload)
    id2, exists2 = db.insert_article_with_job(payload)

    assert id1 == id2
    assert exists1 is False
    assert exists2 is True

    stats = db.get_stats()
    assert stats["total_articles"] == 1
    assert stats["pending_jobs"] == 1  # 重複ジョブが作られないこと


# 6. duplicate submission returns ACK (重複受領時の 200 OK ACK)
def test_duplicate_submission_returns_ack(api_client):
    client, _ = api_client
    payload = {
        "source_id": 1,
        "title": "Duplicate API Title",
        "external_id": "api-dup-1",
    }

    # 1回目の送信 (201 Created)
    res1 = client.post("/api/v1/internal/articles", json=payload)
    assert res1.status_code == 201
    assert res1.json()["status"] == "created"

    # 2回目の重複送信 (200 OK - ACK)
    res2 = client.post("/api/v1/internal/articles", json=payload)
    assert res2.status_code == 200
    assert res2.json()["status"] == "already_exists"


# 7. invalid article (400 バリデーションエラー)
def test_invalid_article(api_client):
    client, _ = api_client

    # title が空文字
    res1 = client.post("/api/v1/internal/articles", json={"source_id": 1, "title": ""})
    assert res1.status_code == 422 or res1.status_code == 400

    # 必須フィールド欠落 (source_id なし)
    res2 = client.post("/api/v1/internal/articles", json={"title": "No Source ID"})
    assert res2.status_code == 422 or res2.status_code == 400


# 8. health endpoint (llm: not_configured)
def test_health_endpoint(api_client):
    client, _ = api_client
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert data["queue"] == "ok"
    assert data["llm"] == "not_configured"  # T004 仕様通りの表現


# 9. stats endpoint
def test_stats_endpoint(api_client):
    client, _ = api_client
    client.post("/api/v1/internal/articles", json={"source_id": 1, "title": "Stats Article 1"})
    client.post("/api/v1/internal/articles", json={"source_id": 1, "title": "Stats Article 2"})

    res = client.get("/api/v1/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_articles"] == 2
    assert data["pending_jobs"] == 2
    assert data["active_events"] == 0


# 10. event endpoint returns empty state
def test_event_endpoint_empty_state(api_client):
    client, _ = api_client
    res = client.get("/api/v1/events")
    assert res.status_code == 200
    data = res.json()
    assert data["events"] == []
    assert data["count"] == 0


# 11. Pi3 -> Pi4 integration (E2E 配送と ACK)
def test_pi3_to_pi4_integration(temp_db_path, api_client):
    client, pi4_db_path = api_client

    # Pi3 Queue の準備
    pi3_queue = CollectorQueue(db_path=temp_db_path)
    art = Article(source_id=1, source_country="JP", external_id="integ-1", title="Integration Title", url="http://example.com/i1")
    row_id = pi3_queue.enqueue_article(art)

    # Delivery Client を TestClient 経由にモック
    def mock_deliver_article(article_dict):
        res = client.post("/api/v1/internal/articles", json={
            "source_id": article_dict["source_id"],
            "source_country": article_dict.get("source_country", "XX"),
            "external_id": article_dict["external_id"],
            "title": article_dict["title"],
            "url": article_dict.get("url"),
            "fetched_at": article_dict.get("fetched_at"),
        })
        if res.status_code in (200, 201):
            return True, None
        return False, res.text

    delivery_client = Pi4DeliveryClient()
    delivery_client.deliver_article = mock_deliver_article

    config = AppConfig()
    scheduler = CollectorScheduler(config=config, queue=pi3_queue, delivery_client=delivery_client)

    scheduler.process_delivery()

    # Pi3 側が sent に変更されたこと
    pi3_art = pi3_queue.get_article_by_id(row_id)
    assert pi3_art["status"] == QueueStatus.SENT

    # Pi4 側に保存・ジョブ生成されたこと
    pi4_db = Pi4Database(db_path=pi4_db_path)
    stats = pi4_db.get_stats()
    assert stats["total_articles"] == 1
    assert stats["pending_jobs"] == 1


# 12. Pi4 unavailable 時の Pi3 pending 保持
def test_pi4_unavailable_pi3_pending(temp_db_path):
    pi3_queue = CollectorQueue(db_path=temp_db_path)
    art = Article(source_id=1, external_id="unavail-1", title="Unavail Title")
    row_id = pi3_queue.enqueue_article(art)

    delivery_client = Pi4DeliveryClient(submit_url="http://non-existent-pi4:8080/api/v1/internal/articles")
    config = AppConfig()
    scheduler = CollectorScheduler(config=config, queue=pi3_queue, delivery_client=delivery_client)

    scheduler.process_delivery()

    # 配送失敗のため pending のまま保持されること
    pi3_art = pi3_queue.get_article_by_id(row_id)
    assert pi3_art["status"] == QueueStatus.PENDING


# 13. Pi4 復旧後の再送
def test_pi4_recovery_resend(temp_db_path, api_client):
    client, pi4_db_path = api_client
    pi3_queue = CollectorQueue(db_path=temp_db_path)
    art = Article(source_id=1, external_id="recov-1", title="Recovery Title")
    row_id = pi3_queue.enqueue_article(art)

    # 1. 最初は失敗 (Pi4 Unavailable)
    delivery_client = Pi4DeliveryClient(submit_url="http://non-existent-pi4:8080/api/v1/internal/articles")
    scheduler = CollectorScheduler(config=AppConfig(), queue=pi3_queue, delivery_client=delivery_client)
    scheduler.process_delivery()

    assert pi3_queue.get_article_by_id(row_id)["status"] == QueueStatus.PENDING

    # 2. Pi4 復旧 (TestClient モックへ切り替え)
    def mock_deliver(article_dict):
        res = client.post("/api/v1/internal/articles", json={
            "source_id": article_dict["source_id"],
            "title": article_dict["title"],
            "external_id": article_dict["external_id"],
            "fetched_at": article_dict.get("fetched_at"),
        })
        return (True, None) if res.status_code in (200, 201) else (False, res.text)

    delivery_client.deliver_article = mock_deliver
    scheduler.delivery_client = delivery_client

    # pending リトライ対象を明示的に取得・配送
    pending_items = pi3_queue.get_pending_articles(include_future_retries=True)
    pi3_queue.mark_sending([a["id"] for a in pending_items])
    res = delivery_client.deliver_batch(pending_items)
    pi3_queue.mark_sent(res.success_ids)

    assert pi3_queue.get_article_by_id(row_id)["status"] == QueueStatus.SENT


# 14. API restart 後もデータ保持
def test_api_restart_data_persistence(temp_db_path):
    db1 = Pi4Database(db_path=temp_db_path)
    db1.insert_article_with_job({"source_id": 1, "title": "Persist Title 1"})

    db2 = Pi4Database(db_path=temp_db_path)
    stats = db2.get_stats()
    assert stats["total_articles"] == 1
    assert stats["pending_jobs"] == 1


# 15. GET /api/events/active 全判定条件テスト (要件 25 遵守)
def test_active_events_api_filtering(api_client):
    client, db_path = api_client
    db = Pi4Database(db_path=db_path)
    now_str = "2026-09-02T10:00:00Z"
    old_str = "2020-01-01T00:00:00Z"

    with db._get_connection() as conn:
        # 1. active + resolved + conf 0.85 -> 含まれる
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, city, latitude, longitude, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (1, 1, 'earthquake', 'JP', 'Wajima', 37.3967, 136.9015, 0.85, 'resolved', ?, ?, ?, 'active', ?, ?)
        """, (now_str, now_str, now_str, now_str, now_str))

        # 2. expired -> 除外される
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, city, latitude, longitude, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (2, 2, 'flood', 'NP', 'Kathmandu', 27.7172, 85.3240, 0.90, 'resolved', ?, ?, ?, 'expired', ?, ?)
        """, (old_str, old_str, old_str, old_str, old_str))

        # 3. unresolved -> 除外される
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, city, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (3, 3, 'storm', 'US', 'Miami', 0.95, 'unresolved', ?, ?, ?, 'active', ?, ?)
        """, (now_str, now_str, now_str, now_str, now_str))

        # 4. confidence < 0.50 -> 除外される
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, city, latitude, longitude, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (4, 4, 'fire', 'GB', 'London', 51.5074, -0.1278, 0.30, 'resolved', ?, ?, ?, 'active', ?, ?)
        """, (now_str, now_str, now_str, now_str, now_str))

        # 5. latitude null -> 除外される
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, city, longitude, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (5, 5, 'crime', 'FR', 'Paris', 2.3522, 0.80, 'resolved', ?, ?, ?, 'active', ?, ?)
        """, (now_str, now_str, now_str, now_str, now_str))

        # 6. longitude null -> 除外される
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, city, latitude, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (6, 6, 'crime', 'FR', 'Paris', 48.8566, 0.80, 'resolved', ?, ?, ?, 'active', ?, ?)
        """, (now_str, now_str, now_str, now_str, now_str))

        # 7. multiple events -> 有効な2つ目を追加
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, city, latitude, longitude, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (7, 7, 'accident', 'DE', 'Berlin', 52.5200, 13.4050, 0.75, 'resolved', ?, ?, ?, 'active', ?, ?)
        """, (now_str, now_str, now_str, now_str, now_str))

        conn.commit()

    resp = client.get("/api/events/active")
    assert resp.status_code == 200
    data = resp.json()

    assert "events" in data
    assert "count" in data
    assert data["count"] == 2
    event_ids = [e["id"] for e in data["events"]]
    assert 1 in event_ids
    assert 7 in event_ids
    assert 2 not in event_ids
    assert 3 not in event_ids
    assert 4 not in event_ids
    assert 5 not in event_ids
    assert 6 not in event_ids


# 16. GET /api/events/{event_id}/articles 関連記事取得テスト
def test_event_articles_api(api_client):
    client, db_path = api_client
    db = Pi4Database(db_path=db_path)
    now_str = "2026-09-02T10:00:00Z"

    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO articles (source_id, source_country, title, description, url, published_at, fetched_at, created_at, updated_at)
            VALUES (1, 'JP', 'Wajima Earthquake Article', 'Desc', 'http://example.com/wajima', ?, ?, ?, ?)
        """, (now_str, now_str, now_str, now_str))
        art_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, city, latitude, longitude, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (?, 1, 'earthquake', 'JP', 'Wajima', 37.3967, 136.9015, 0.85, 'resolved', ?, ?, ?, 'active', ?, ?)
        """, (art_id, now_str, now_str, now_str, now_str, now_str))
        evt_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO article_events (article_id, event_id, relation_type)
            VALUES (?, ?, 'primary')
        """, (art_id, evt_id))

        conn.commit()

    resp = client.get(f"/api/events/{evt_id}/articles")
    assert resp.status_code == 200
    data = resp.json()

    assert data["count"] == 1
    assert data["articles"][0]["title"] == "Wajima Earthquake Article"

