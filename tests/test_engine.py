"""Event Engine 単体テストスイート (Matching, Merge, Expiration & Active Query)"""

import pytest
from datetime import datetime, timezone, timedelta
from world_news.schemas import EventCategory, EventStatus, EventMatchingConfig
from world_news.api.database import Pi4Database
from world_news.engine.matcher import calculate_haversine_distance, is_same_event
from world_news.engine.engine import EventEngine
from world_news.engine.worker import EventEngineWorker


@pytest.fixture
def test_db(tmp_path):
    db_path = tmp_path / "test_engine.db"
    return Pi4Database(db_path=db_path)


# 1. Haversine 距離計算テスト
def test_haversine_distance():
    # 東京駅 (35.6812, 139.7671) と 横浜駅 (35.4658, 139.6223) -> 約 27.5 km
    dist_tokyo_yokohama = calculate_haversine_distance(35.6812, 139.7671, 35.4658, 139.6223)
    assert 25.0 <= dist_tokyo_yokohama <= 30.0

    # 東京駅 (35.6812, 139.7671) と 大阪駅 (34.7024, 135.4959) -> 約 396 km
    dist_tokyo_osaka = calculate_haversine_distance(35.6812, 139.7671, 34.7024, 135.4959)
    assert 380.0 <= dist_tokyo_osaka <= 410.0


# 2. 同一事件のマッチングテスト (近接場所)
def test_event_matching_same_location():
    now_str = datetime.now(timezone.utc).isoformat()
    evt1 = {
        "event_type": "earthquake",
        "country_code": "JP",
        "latitude": 37.3967,
        "longitude": 136.9015,
        "first_seen_at": now_str,
    }
    # 輪島から 10km 離れた場所
    evt2 = {
        "event_type": "earthquake",
        "country_code": "JP",
        "latitude": 37.4500,
        "longitude": 136.9500,
        "first_seen_at": now_str,
    }

    assert is_same_event(evt1, evt2) is True


# 3. 異事件のマッチング除外テスト (遠隔地)
def test_event_matching_different_location():
    now_str = datetime.now(timezone.utc).isoformat()
    evt1 = {
        "event_type": "earthquake",
        "country_code": "JP",
        "latitude": 35.6812,  # 東京
        "longitude": 139.7671,
        "first_seen_at": now_str,
    }
    evt2 = {
        "event_type": "earthquake",
        "country_code": "JP",
        "latitude": 34.7024,  # 大阪
        "longitude": 135.4959,
        "first_seen_at": now_str,
    }

    assert is_same_event(evt1, evt2) is False


# 4. イベントマージ・信頼度更新・延命テスト
def test_event_merge(test_db):
    engine = EventEngine(db=test_db)
    now_str = datetime.now(timezone.utc).isoformat()

    # 1. 最初のイベント登録
    with test_db._get_connection() as conn:
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, city, latitude, longitude, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (1, 1, 'flood', 'NP', 'Kathmandu', 27.7172, 85.3240, 0.70, 'resolved', ?, ?, ?, 'active', ?, ?)
        """, (now_str, now_str, now_str, now_str, now_str))
        conn.commit()

    # 近接する新しい記事からのイベントデータ
    new_evt = {
        "article_id": 2,
        "event_type": "flood",
        "country_code": "NP",
        "city": "Kathmandu",
        "latitude": 27.7200,
        "longitude": 85.3250,
        "confidence": 0.85,  # 信頼度更新
        "first_seen_at": now_str,
    }

    event_id, is_merged = engine.process_new_event(new_evt)
    assert is_merged is True
    assert event_id == 1

    # DB 内の信頼度と last_seen_at が更新されていること
    active_evts = test_db.get_active_events()
    assert len(active_evts) == 1
    assert active_evts[0]["confidence"] == 0.85


# 5. 有効期限判定 (6時間経過後の expired 切替)
def test_event_expiration(test_db):
    worker = EventEngineWorker(db=test_db)

    # 過去 10 時間前のイベント
    old_dt = datetime.now(timezone.utc) - timedelta(hours=10)
    old_str = old_dt.isoformat()

    with test_db._get_connection() as conn:
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, latitude, longitude, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (1, 1, 'accident', 'US', 35.0, 139.0, 0.80, 'resolved', ?, ?, ?, 'active', ?, ?)
        """, (old_str, old_str, old_str, old_str, old_str))
        conn.commit()

    assert len(test_db.get_active_events()) == 1

    expired_count = worker.run_expiration_check()
    assert expired_count == 1
    assert len(test_db.get_active_events()) == 0


# 6. 地図用アクティブイベント抽出テスト
def test_get_active_events(test_db):
    now_str = datetime.now(timezone.utc).isoformat()

    with test_db._get_connection() as conn:
        # アクティブ & 解決済み & 高信頼度 -> 抽出対象
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, latitude, longitude, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (1, 1, 'storm', 'JP', 35.6895, 139.6917, 0.90, 'resolved', ?, ?, ?, 'active', ?, ?)
        """, (now_str, now_str, now_str, now_str, now_str))

        # 未解決 (unresolved) -> 抽出対象外
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (2, 2, 'storm', 'JP', 0.90, 'unresolved', ?, ?, ?, 'active', ?, ?)
        """, (now_str, now_str, now_str, now_str, now_str))

        # 低信頼度 (<0.50) -> 抽出対象外
        conn.execute("""
            INSERT INTO events (article_id, analysis_id, event_type, country_code, latitude, longitude, confidence, geocoding_status, first_seen_at, last_seen_at, expires_at, status, created_at, updated_at)
            VALUES (3, 3, 'storm', 'JP', 35.6895, 139.6917, 0.30, 'resolved', ?, ?, ?, 'active', ?, ?)
        """, (now_str, now_str, now_str, now_str, now_str))

        conn.commit()

    active_evts = test_db.get_active_events(min_confidence=0.50)
    assert len(active_evts) == 1
    assert active_evts[0]["article_id"] == 1
