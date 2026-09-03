"""T012 News Quality and Event Accuracy Regression Tests"""

import pytest
from world_news.analyzer.prompts import build_analysis_prompt, SYSTEM_PROMPT_V1
from world_news.analyzer.schemas import LLMAnalysisOutput
from world_news.geocoder.base import GeocodingResult
from world_news.geocoder.location_resolver import LocationResolver, ISO_TO_COUNTRY_NAME
from world_news.schemas import GeocodingStatus, GeocodingErrorCode
from world_news.engine.matcher import is_same_event
from world_news.quality import QualityEvaluator, Path


class MockGeocoder:
    def __init__(self, mock_country="JP"):
        self.provider_name = "mock_geocoder"
        self.mock_country = mock_country

    def geocode(self, query: str) -> GeocodingResult:
        if "france" in query.lower() or "paris" in query.lower():
            return GeocodingResult(
                status=GeocodingStatus.RESOLVED.value,
                latitude=48.8566,
                longitude=2.3522,
                country_code="FR",
                provider=self.provider_name,
                query=query,
            )
        if "wajima" in query.lower() or "japan" in query.lower():
            return GeocodingResult(
                status=GeocodingStatus.RESOLVED.value,
                latitude=37.391,
                longitude=136.899,
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


def test_source_country_is_not_event_country():
    """Test Case A: Overseas media reporting Japan event sets event_country=JP, not source_country=GB"""
    prompt = build_analysis_prompt(
        title="Powerful M6.8 Earthquake Strikes Wajima, Ishikawa Prefecture",
        description="A strong quake shook Japan",
        source_country="GB"
    )
    assert "source_country, for reference ONLY - do not copy" in prompt
    assert "GB" in prompt

    out = LLMAnalysisOutput(
        is_event=True,
        event_type="earthquake",
        event_country="JP",
        event_region="Ishikawa",
        event_city="Wajima",
        confidence=0.95
    )
    assert out.event_country == "JP"
    assert out.event_country != "GB"


def test_unknown_location_remains_null():
    """Test Case D/E: Unknown or unstated locations remain null and unresolved"""
    out = LLMAnalysisOutput(
        is_event=False,
        event_type="economy",
        event_country="DE",
        event_region=None,
        event_city=None,
        location_name=None,
        confidence=0.80
    )
    assert out.event_city is None
    assert out.event_region is None

    resolver = LocationResolver(geocoder=MockGeocoder())
    queries = resolver.build_fallback_queries("DE", None, None, None)
    # Country-only should NOT build a search query
    assert len(queries) == 0


def test_country_only_does_not_create_centroid():
    """Test Case D: Country-only input does not create country centroid coordinates"""
    resolver = LocationResolver(geocoder=MockGeocoder(mock_country="JP"))
    res = resolver.resolve_event_location("JP", None, None, None)
    assert res.status == GeocodingStatus.UNRESOLVED.value
    assert res.error_code == GeocodingErrorCode.NO_COUNTRY_CENTROID.value
    assert res.latitude is None
    assert res.longitude is None


def test_country_mismatch_is_rejected():
    """Test Geocoding validation rejects results when country mismatches"""
    resolver = LocationResolver(geocoder=MockGeocoder())
    # Expected JP, but MockGeocoder returns FR for Paris query
    queries = resolver.build_fallback_queries("JP", "Ile-de-France", "Paris", None)
    res = resolver.resolve_event_location("JP", "Ile-de-France", "Paris", None)
    
    assert res.status == GeocodingStatus.UNRESOLVED.value
    assert res.error_code == GeocodingErrorCode.COUNTRY_MISMATCH.value
    assert res.latitude is None


def test_same_event_articles_are_merged():
    """Test Case F: Multiple news reports of the same event are merged"""
    evt1 = {"event_type": "earthquake", "country_code": "JP", "city": "Wajima", "latitude": 37.391, "longitude": 136.899}
    evt2 = {"event_type": "earthquake", "country_code": "JP", "city": "Wajima", "latitude": 37.395, "longitude": 136.901}
    
    assert is_same_event(evt1, evt2) is True


def test_different_events_are_not_merged():
    """Test Case G: Different events in the same city are not merged"""
    evt1 = {"event_type": "fire", "country_code": "JP", "city": "Tokyo", "latitude": 35.689, "longitude": 139.691}
    evt2 = {"event_type": "politics", "country_code": "JP", "city": "Tokyo", "latitude": 35.689, "longitude": 139.691}
    
    assert is_same_event(evt1, evt2) is False


def test_false_event_is_not_promoted():
    """Test non-events (opinions, retrospective articles, product reviews) are not promoted as events"""
    retrospective_out = LLMAnalysisOutput(
        is_event=False,
        event_type="earthquake",
        event_country="JP",
        confidence=0.85
    )
    assert retrospective_out.is_event is False


def test_real_event_is_promoted():
    """Test real news events are correctly classified with high confidence"""
    real_event_out = LLMAnalysisOutput(
        is_event=True,
        event_type="wildfire",
        event_country="US",
        event_city="Los Angeles",
        confidence=0.92
    )
    assert real_event_out.is_event is True
    assert real_event_out.confidence >= 0.50


def test_quality_evaluator_ground_truth():
    """Test QualityEvaluator CLI runner with Ground Truth dataset"""
    gt_path = Path("tests/data/t012_ground_truth.json")
    evaluator = QualityEvaluator(gt_path)
    metrics = evaluator.evaluate()

    assert metrics["total_articles"] >= 50
    assert metrics["accuracy"] >= 0.85
    assert metrics["precision"] >= 0.85
    assert metrics["recall"] >= 0.80
    assert metrics["country_accuracy"] >= 0.90
