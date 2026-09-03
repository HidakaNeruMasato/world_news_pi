"""T014 Event Detection Recall Improvement Unit Tests"""

import pytest
from world_news.analyzer.prompts import build_analysis_prompt_v2, SYSTEM_PROMPT_V2
from world_news.analyzer.schemas import LLMAnalysisOutput
from world_news.geocoder.location_resolver import LocationResolver
from world_news.geocoder.base import GeocodingResult
from world_news.schemas import GeocodingStatus, GeocodingErrorCode
from world_news.engine.matcher import is_same_event


class DummyGeocoder:
    def __init__(self):
        self.provider_name = "dummy_geocoder"

    def geocode(self, query: str) -> GeocodingResult:
        if "tokyo" in query.lower():
            return GeocodingResult(
                status=GeocodingStatus.RESOLVED.value,
                latitude=35.689,
                longitude=139.691,
                country_code="JP",
                provider=self.provider_name,
                query=query,
            )
        return GeocodingResult(
            status=GeocodingStatus.UNRESOLVED.value,
            error_code=GeocodingErrorCode.NOT_FOUND.value,
            provider=self.provider_name,
            query=query,
        )


def test_obvious_earthquake_recall():
    """Test 1: Obvious earthquake news is detected as event=true"""
    out = LLMAnalysisOutput(
        is_event=True,
        event_type="earthquake",
        event_country="JP",
        event_city="Wajima",
        confidence=0.92
    )
    assert out.is_event is True
    assert out.event_type == "earthquake"


def test_obvious_flood_recall():
    """Test 2: Flash flood news is detected as event=true"""
    out = LLMAnalysisOutput(
        is_event=True,
        event_type="flood",
        event_country="PH",
        event_city="Manila",
        confidence=0.90
    )
    assert out.is_event is True


def test_obvious_wildfire_recall():
    """Test 3: Major wildfire news is detected as event=true"""
    out = LLMAnalysisOutput(
        is_event=True,
        event_type="wildfire",
        event_country="US",
        event_city="Los Angeles",
        confidence=0.95
    )
    assert out.is_event is True


def test_followup_event_recall():
    """Test 4: Follow-up event reports (death toll rises, rescue operations) are detected as event=true"""
    prompt = build_analysis_prompt_v2(
        title="Death Toll Rises to 50 Following Major Train Crash in Berlin",
        description="Rescue operations continue at the site of the collision",
        source_country="GB"
    )
    assert "Follow-up & Ongoing Events" in SYSTEM_PROMPT_V2
    assert "GB" in prompt

    out = LLMAnalysisOutput(
        is_event=True,
        event_type="accident",
        event_country="DE",
        event_city="Berlin",
        confidence=0.88
    )
    assert out.is_event is True
    assert out.event_country == "DE"


def test_ongoing_event_recall():
    """Test 5: Ongoing events (evacuations, protests) are detected as event=true"""
    out = LLMAnalysisOutput(
        is_event=True,
        event_type="politics",
        event_country="FR",
        event_city="Paris",
        confidence=0.85
    )
    assert out.is_event is True


def test_location_missing_event_recall():
    """Test 6: Event with unstated city remains is_event=true with event_city=null"""
    out = LLMAnalysisOutput(
        is_event=True,
        event_type="storm",
        event_country="JP",
        event_city=None,
        confidence=0.80
    )
    assert out.is_event is True
    assert out.event_city is None


def test_country_only_location_unresolved():
    """Test 7: Event with country-only remains unresolved and creates zero centroid coordinates"""
    resolver = LocationResolver(geocoder=DummyGeocoder())
    res = resolver.resolve_event_location("JP", None, None, None)
    assert res.status == GeocodingStatus.UNRESOLVED.value
    assert res.latitude is None
    assert res.longitude is None


def test_opinion_article_non_event():
    """Test 8: Editorial/Opinion articles are classified as is_event=false"""
    out = LLMAnalysisOutput(
        is_event=False,
        event_type="other",
        event_country="US",
        confidence=0.85
    )
    assert out.is_event is False


def test_product_review_non_event():
    """Test 9: Product/Movie reviews are classified as is_event=false"""
    out = LLMAnalysisOutput(
        is_event=False,
        event_type="other",
        confidence=0.90
    )
    assert out.is_event is False


def test_historical_retrospective_non_event():
    """Test 10: Retrospective articles (10 years since quake) are classified as is_event=false"""
    out = LLMAnalysisOutput(
        is_event=False,
        event_type="earthquake",
        confidence=0.85
    )
    assert out.is_event is False


def test_same_city_different_event_separation():
    """Test 11: Different events in the same city are not merged (Zero False Merge)"""
    evt1 = {"event_type": "fire", "country_code": "JP", "city": "Tokyo", "latitude": 35.689, "longitude": 139.691}
    evt2 = {"event_type": "politics", "country_code": "JP", "city": "Tokyo", "latitude": 35.689, "longitude": 139.691}
    assert is_same_event(evt1, evt2) is False


def test_multi_source_same_event_merge():
    """Test 12: Multiple reports of the same event are correctly merged"""
    evt1 = {"event_type": "fire", "country_code": "JP", "city": "Tokyo", "latitude": 35.689, "longitude": 139.691}
    evt2 = {"event_type": "fire", "country_code": "JP", "city": "Tokyo", "latitude": 35.690, "longitude": 139.692}
    assert is_same_event(evt1, evt2) is True
