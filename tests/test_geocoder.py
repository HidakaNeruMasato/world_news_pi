"""Geocoding & Location Resolver 全18ケース単体テストスイート"""

import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from world_news.schemas import EventCategory, GeocodingStatus, GeocodingErrorCode, Event
from world_news.api.database import Pi4Database
from world_news.geocoder.base import BaseGeocoder, GeocodingResult
from world_news.geocoder.nominatim import NominatimGeocoder
from world_news.geocoder.location_resolver import LocationResolver, get_country_name
from world_news.geocoder.worker import EventGeocoderWorker


class MockGeocoder(BaseGeocoder):
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.call_count = 0

    @property
    def provider_name(self) -> str:
        return "mock_geocoder"

    def geocode(self, query: str) -> GeocodingResult:
        self.call_count += 1
        if query in self.responses:
            res = self.responses[query]
            res.provider = self.provider_name
            res.query = query
            return res
        return GeocodingResult(
            status=GeocodingStatus.UNRESOLVED.value,
            error_code=GeocodingErrorCode.NOT_FOUND.value,
            provider=self.provider_name,
            query=query,
        )


@pytest.fixture
def test_db(tmp_path):
    db_path = tmp_path / "test_geocoder.db"
    db = Pi4Database(db_path=db_path)
    return db


# 1. Geocoder interface abstraction
def test_geocoder_interface_abstraction():
    geocoder = MockGeocoder()
    assert geocoder.provider_name == "mock_geocoder"
    res = geocoder.geocode("Tokyo, Japan")
    assert isinstance(res, GeocodingResult)
    assert res.status == GeocodingStatus.UNRESOLVED.value


# 2. successful geocoding
def test_successful_geocoding():
    mock_res = GeocodingResult(
        latitude=35.6895,
        longitude=139.6917,
        country_code="JP",
        country_name="Japan",
        display_name="Tokyo, Japan",
        status=GeocodingStatus.RESOLVED.value,
        error_code=GeocodingErrorCode.RESOLVED.value,
    )
    geocoder = MockGeocoder({"Tokyo, Japan": mock_res})
    resolver = LocationResolver(geocoder)

    res = resolver.resolve_event_location(
        event_country="JP", event_region="Tokyo", event_city="Tokyo", location_name=None
    )
    assert res.status == GeocodingStatus.RESOLVED.value
    assert res.latitude == 35.6895
    assert res.longitude == 139.6917
    assert res.country_code == "JP"


# 3. unresolved location
def test_unresolved_location():
    geocoder = MockGeocoder()
    resolver = LocationResolver(geocoder)
    res = resolver.resolve_event_location(
        event_country="XX", event_region="UnknownRegion", event_city="UnknownCity", location_name=None
    )
    assert res.status == GeocodingStatus.UNRESOLVED.value
    assert res.error_code == GeocodingErrorCode.NOT_FOUND.value


# 4. network error
def test_network_error_handling():
    mock_res = GeocodingResult(
        status=GeocodingStatus.UNRESOLVED.value,
        error_code=GeocodingErrorCode.NETWORK_ERROR.value,
    )
    geocoder = MockGeocoder({"Paris, France": mock_res})
    resolver = LocationResolver(geocoder)
    res = resolver.resolve_event_location("FR", "IDF", "Paris", None)
    assert res.status == GeocodingStatus.UNRESOLVED.value
    assert res.error_code == GeocodingErrorCode.NETWORK_ERROR.value


# 5. timeout
def test_timeout_handling():
    mock_res = GeocodingResult(
        status=GeocodingStatus.UNRESOLVED.value,
        error_code=GeocodingErrorCode.TIMEOUT.value,
    )
    geocoder = MockGeocoder({"London, United Kingdom": mock_res})
    resolver = LocationResolver(geocoder)
    res = resolver.resolve_event_location("GB", "England", "London", None)
    assert res.status == GeocodingStatus.UNRESOLVED.value
    assert res.error_code == GeocodingErrorCode.TIMEOUT.value


# 6. rate limit
def test_rate_limit_handling():
    mock_res = GeocodingResult(
        status=GeocodingStatus.UNRESOLVED.value,
        error_code=GeocodingErrorCode.RATE_LIMITED.value,
    )
    geocoder = MockGeocoder({"Berlin, Germany": mock_res})
    resolver = LocationResolver(geocoder)
    res = resolver.resolve_event_location("DE", "Berlin", "Berlin", None)
    assert res.status == GeocodingStatus.UNRESOLVED.value
    assert res.error_code == GeocodingErrorCode.RATE_LIMITED.value


# 7. retry
def test_worker_retry(test_db):
    # 最初はエラー、2回目は成功
    mock_res_fail = GeocodingResult(
        status=GeocodingStatus.UNRESOLVED.value,
        error_code=GeocodingErrorCode.NETWORK_ERROR.value,
    )
    mock_res_ok = GeocodingResult(
        latitude=40.7128,
        longitude=-74.0060,
        country_code="US",
        display_name="New York, United States",
        status=GeocodingStatus.RESOLVED.value,
        error_code=GeocodingErrorCode.RESOLVED.value,
    )
    geocoder = MockGeocoder({"New York, United States": mock_res_fail})
    worker = EventGeocoderWorker(db=test_db, geocoder=geocoder)

    evt_payload = {
        "article_id": 1,
        "analysis_id": 1,
        "event_type": EventCategory.ACCIDENT,
        "country_code": "US",
        "city": "New York",
        "geocoding_status": "unresolved",
    }
    # イベント作成
    now_str = "2026-01-01T00:00:00Z"
    with test_db._get_connection() as conn:
        conn.execute(
            "INSERT INTO events (article_id, analysis_id, event_type, country_code, city, geocoding_status, first_seen_at, last_seen_at, created_at, updated_at) VALUES (1, 1, 'accident', 'US', 'New York', 'unresolved', ?, ?, ?, ?)",
            (now_str, now_str, now_str, now_str)
        )
        conn.commit()

    evts = test_db.get_unresolved_events()
    res1 = worker.process_event(evts[0])
    assert res1.status == GeocodingStatus.UNRESOLVED.value

    # 応答を成功に切替えて再試行 (Retry)
    geocoder.responses["New York, United States"] = mock_res_ok
    res2 = worker.process_event(evts[0])
    assert res2.status == GeocodingStatus.RESOLVED.value
    assert res2.latitude == 40.7128


# 8. cache hit & 9. cache miss
def test_cache_hit_and_miss(test_db):
    mock_res = GeocodingResult(
        latitude=35.6895,
        longitude=139.6917,
        country_code="JP",
        display_name="Tokyo, Japan",
        raw_json={"address": {"country_code": "jp"}},
        status=GeocodingStatus.RESOLVED.value,
        error_code=GeocodingErrorCode.RESOLVED.value,
    )
    geocoder = MockGeocoder({"Tokyo, Japan": mock_res})
    worker = EventGeocoderWorker(db=test_db, geocoder=geocoder)

    evt = {
        "id": 1,
        "country_code": "JP",
        "city": "Tokyo",
        "region": None,
        "location_name": None,
    }

    # 初回: Cache miss -> Geocoder 呼び出し
    res1 = worker.process_event(evt)
    assert geocoder.call_count == 1
    assert res1.status == GeocodingStatus.RESOLVED.value

    # 2回目: Cache hit -> Geocoder 呼び出しなし
    res2 = worker.process_event(evt)
    assert geocoder.call_count == 1  # 増加しない
    assert res2.status == GeocodingStatus.RESOLVED.value
    assert res2.latitude == 35.6895


# 10. country match
def test_country_match():
    resolver = LocationResolver(MockGeocoder())
    assert resolver.validate_country_match("JP", "JP") is True
    assert resolver.validate_country_match("US", "US") is True
    assert resolver.validate_country_match("GB", "UK") is True


# 11. country mismatch
def test_country_mismatch():
    mock_res = GeocodingResult(
        latitude=38.8951,
        longitude=-77.0364,
        country_code="US",  # USA にヒット
        display_name="Washington, USA",
        status=GeocodingStatus.RESOLVED.value,
        error_code=GeocodingErrorCode.RESOLVED.value,
    )
    # LLM は JP の Wajima と言っているのに US の Washington に Geocode されたケース
    geocoder = MockGeocoder({"Washington, Japan": mock_res})
    resolver = LocationResolver(geocoder)

    res = resolver.resolve_event_location("JP", None, "Washington", None)
    assert res.status == GeocodingStatus.UNRESOLVED.value
    assert res.error_code == GeocodingErrorCode.COUNTRY_MISMATCH.value


# 12. fallback query
def test_fallback_query_building():
    resolver = LocationResolver(MockGeocoder())
    queries = resolver.build_fallback_queries("JP", "Ishikawa", "Wajima", "Asaichi Market")
    assert "Asaichi Market, Wajima, Ishikawa, Japan" in queries
    assert "Wajima, Ishikawa, Japan" in queries
    assert "Wajima, Japan" in queries
    assert "Ishikawa, Japan" in queries
    assert "Japan" not in queries  # 国単体は除外されていること


# 13. no country centroid fallback
def test_no_country_centroid_fallback():
    geocoder = MockGeocoder()
    resolver = LocationResolver(geocoder)

    # 国名 JP のみ判明しているイベント
    res = resolver.resolve_event_location("JP", None, None, None)
    assert res.status == GeocodingStatus.UNRESOLVED.value
    assert res.error_code == GeocodingErrorCode.NO_COUNTRY_CENTROID.value
    assert res.latitude is None
    assert res.longitude is None


# 14. latitude validation & 15. longitude validation & 16. invalid coordinate rejection
def test_coordinate_validations():
    resolver = LocationResolver(MockGeocoder())
    assert resolver.validate_coordinates(35.0, 139.0) is True
    assert resolver.validate_coordinates(-90.0, -180.0) is True
    assert resolver.validate_coordinates(90.0, 180.0) is True
    assert resolver.validate_coordinates(91.0, 139.0) is False   # 無効な緯度
    assert resolver.validate_coordinates(35.0, 181.0) is False  # 無効な経度
    assert resolver.validate_coordinates(None, 139.0) is False

    mock_res_invalid = GeocodingResult(
        latitude=999.0,
        longitude=139.0,
        country_code="JP",
        status=GeocodingStatus.RESOLVED.value,
    )
    geocoder = MockGeocoder({"Tokyo, Japan": mock_res_invalid})
    resolver_invalid = LocationResolver(geocoder)
    res = resolver_invalid.resolve_event_location("JP", None, "Tokyo", None)
    assert res.status == GeocodingStatus.UNRESOLVED.value
    assert res.error_code == GeocodingErrorCode.INVALID_COORDINATE.value


# 17. event schema migration
def test_event_schema_migration(test_db):
    evt = Event(
        event_type=EventCategory.FLOOD,
        country_code="NP",
        city="Kathmandu",
        geocoding_status="unresolved",
    )
    assert evt.geocoding_status == "unresolved"
    assert evt.geocoding_provider is None

    test_db.update_event_geocoding_result(
        event_id=1,
        geocoding_status="resolved",
        latitude=27.7172,
        longitude=85.3240,
        provider="nominatim",
        query="Kathmandu, Nepal",
        display_name="Kathmandu, Nepal",
        error_code="resolved",
    )


# 18. existing unresolved event retry
def test_existing_unresolved_event_retry(test_db):
    now_str = "2026-01-01T00:00:00Z"
    with test_db._get_connection() as conn:
        conn.execute(
            "INSERT INTO events (article_id, analysis_id, event_type, country_code, city, geocoding_status, first_seen_at, last_seen_at, created_at, updated_at) VALUES (1, 1, 'flood', 'NP', 'Kathmandu', 'unresolved', ?, ?, ?, ?)",
            (now_str, now_str, now_str, now_str)
        )
        conn.commit()

    unresolved = test_db.get_unresolved_events()
    assert len(unresolved) == 1
    assert unresolved[0]["city"] == "Kathmandu"
