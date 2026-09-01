"""共通データ構造およびスキーマ定義 (Pydantic models & Enums)"""

from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class EventCategory(str, Enum):
    """SPEC.md §5 に定義されたイベントカテゴリ"""
    EARTHQUAKE = "earthquake"
    VOLCANIC = "volcanic"
    TSUNAMI = "tsunami"
    FLOOD = "flood"
    STORM = "storm"
    WILDFIRE = "wildfire"
    FIRE = "fire"
    EXPLOSION = "explosion"
    TRAFFIC_ACCIDENT = "traffic_accident"
    RAIL_ACCIDENT = "rail_accident"
    AVIATION_ACCIDENT = "aviation_accident"
    MARITIME_ACCIDENT = "maritime_accident"
    INDUSTRIAL_ACCIDENT = "industrial_accident"
    CRIME = "crime"
    SHOOTING = "shooting"
    TERRORISM = "terrorism"
    PROTEST = "protest"
    WAR = "war"
    MILITARY = "military"
    OTHER = "other"
    NONE = "none"


class ArticleProcessingStatus(str, Enum):
    """記事の処理状態"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    FAILED = "failed"


class EventStatus(str, Enum):
    """イベントの表示状態"""
    ACTIVE = "active"
    EXPIRED = "expired"
    RESOLVED = "resolved"


class Source(BaseModel):
    """RSS配信元情報モデル (DATABASE.md §2)"""
    id: Optional[int] = None
    name: str
    country_code: Optional[str] = None
    language: Optional[str] = None
    feed_url: str
    category: Optional[str] = None
    enabled: bool = True
    interval_seconds: Optional[int] = 300
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None


class Article(BaseModel):
    """収集記事モデル (DATABASE.md §3)"""
    id: Optional[int] = None
    source_id: int
    external_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    fetched_at: datetime = Field(default_factory=datetime.now)
    language: Optional[str] = None
    content_hash: Optional[str] = None
    processing_status: ArticleProcessingStatus = ArticleProcessingStatus.PENDING
    retry_count: int = 0
    event_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Analysis(BaseModel):
    """LLM解析結果モデル (DATABASE.md §4)"""
    id: Optional[int] = None
    article_id: int
    model_id: Optional[str] = None
    model_version: Optional[str] = None
    prompt_version: Optional[str] = None
    raw_output: Optional[str] = None
    parsed_json: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None
    analyzed_at: datetime = Field(default_factory=datetime.now)


class Event(BaseModel):
    """正規化イベントモデル (DATABASE.md §5)"""
    id: Optional[int] = None
    event_type: EventCategory
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    location_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    first_seen_at: datetime = Field(default_factory=datetime.now)
    last_seen_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime
    status: EventStatus = EventStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class HealthStatus(BaseModel):
    """ヘルスチェック応答モデル (API.md §2)"""
    status: str = "ok"
    database: str = "ok"
    llm: str = "ok"
    queue: str = "ok"
