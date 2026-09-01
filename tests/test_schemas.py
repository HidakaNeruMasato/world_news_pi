"""共通スキーマのユニットテスト"""

from datetime import datetime, timedelta
import pytest
from pydantic import ValidationError
from world_news.schemas import (
    EventCategory,
    ArticleProcessingStatus,
    EventStatus,
    Source,
    Article,
    Event,
    HealthStatus,
)


def test_event_category_enum():
    """EventCategory の列挙型検証"""
    assert EventCategory.EARTHQUAKE == "earthquake"
    assert EventCategory.WAR == "war"
    assert EventCategory.NONE == "none"


def test_article_schema():
    """Article モデルの生成・初期値の確認"""
    article = Article(
        source_id=1,
        title="テストニュース",
        url="https://example.com/news/1",
    )
    assert article.source_id == 1
    assert article.title == "テストニュース"
    assert article.processing_status == ArticleProcessingStatus.PENDING
    assert article.retry_count == 0


def test_event_schema_validation():
    """Event モデルのバリデーション確認"""
    now = datetime.now()
    expires = now + timedelta(hours=6)

    event = Event(
        event_type=EventCategory.FLOOD,
        country_code="JP",
        confidence=0.95,
        expires_at=expires,
    )
    assert event.event_type == EventCategory.FLOOD
    assert event.confidence == 0.95
    assert event.status == EventStatus.ACTIVE

    # confidence の範囲外エラー (1.00 超え) の検証
    with pytest.raises(ValidationError):
        Event(
            event_type=EventCategory.FLOOD,
            confidence=1.5,
            expires_at=expires,
        )


def test_health_status_schema():
    """HealthStatus モデルの確認"""
    health = HealthStatus()
    assert health.status == "ok"
    assert health.database == "ok"
    assert health.llm == "ok"
    assert health.queue == "ok"
