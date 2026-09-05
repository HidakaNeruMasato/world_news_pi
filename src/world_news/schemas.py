"""共通データ構造およびスキーマ定義 (Pydantic models & Enums)"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EventCategory(str, Enum):
    """イベントカテゴリ enum"""
    EARTHQUAKE = "earthquake"
    TSUNAMI = "tsunami"
    VOLCANIC_ERUPTION = "volcanic_eruption"
    FLOOD = "flood"
    WILDFIRE = "wildfire"
    STORM = "storm"
    ACCIDENT = "accident"
    AVIATION_ACCIDENT = "aviation_accident"
    MARITIME_ACCIDENT = "maritime_accident"
    CRIME = "crime"
    TERRORISM = "terrorism"
    ARMED_CONFLICT = "armed_conflict"
    WAR = "war"
    EXPLOSION = "explosion"
    FIRE = "fire"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    POLITICS = "politics"
    ECONOMY = "economy"
    SPORTS = "sports"
    OTHER = "other"
    NONE = "none"


class ArticleProcessingStatus(str, Enum):
    """記事の処理状態"""
    PENDING = "pending"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    FAILED = "failed"


class JobStatus(str, Enum):
    """Processing Job の処理状態"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EventStatus(str, Enum):
    """イベントの表示状態"""
    ACTIVE = "active"
    EXPIRED = "expired"
    RESOLVED = "resolved"


class EventMatchingConfig(BaseModel):
    """イベント照合・マージ設定"""
    max_distance_km: float = 50.0       # 同一事件とみなす最大距離 (km)
    max_time_diff_hours: float = 24.0   # 同一事件とみなす最大時間差 (時間)
    default_lifetime_hours: float = 6.0 # イベント表示デフォルト有効期限 (時間)
    min_confidence: float = 0.50        # 表示最小信頼度


class GeocodingStatus(str, Enum):
    """Geocoding 処理ステータス"""
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    FAILED = "failed"


class GeocodingErrorCode(str, Enum):
    """Geocoding 詳細エラーコード"""
    RESOLVED = "resolved"
    NOT_FOUND = "not_found"
    COUNTRY_MISMATCH = "country_mismatch"
    NO_COUNTRY_CENTROID = "no_country_centroid"
    NETWORK_ERROR = "network_error"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    INVALID_COORDINATE = "invalid_coordinate"


class AnalysisErrorCode(str, Enum):
    """LLM解析・バリデーションエラーコード"""
    MODEL_UNAVAILABLE = "model_unavailable"
    TIMEOUT = "timeout"
    MALFORMED_OUTPUT = "malformed_output"
    JSON_PARSE_FAILURE = "json_parse_failure"
    SCHEMA_VALIDATION_FAILURE = "schema_validation_failure"
    UNEXPECTED_RUNTIME_ERROR = "unexpected_runtime_error"


class Source(BaseModel):
    """RSS配信元情報モデル"""
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
    """収集記事モデル"""
    id: Optional[int] = None
    source_id: int
    source_country: Optional[str] = None
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
    """LLM解析結果モデル (DATABASE.md §4 拡張)"""
    id: Optional[int] = None
    article_id: int
    model_name: str = "Qwen2.5-1.5B-Instruct-GGUF"
    model_version: Optional[str] = "Q4_K_M"
    prompt_version: str = "analysis_prompt_v1"
    raw_output: Optional[str] = None
    parsed_output: Optional[Dict[str, Any]] = None
    is_event: bool = False
    event_type: Optional[str] = None
    event_country: Optional[str] = None
    event_region: Optional[str] = None
    event_city: Optional[str] = None
    location_name: Optional[str] = None
    confidence: float = 0.0
    error_code: Optional[str] = None
    inference_time_ms: float = 0.0
    analyzed_at: datetime = Field(default_factory=datetime.now)


class Event(BaseModel):
    """正規化イベントモデル (DATABASE.md §5 拡張 + T007 Geocoding 拡張)"""
    id: Optional[int] = None
    article_id: Optional[int] = None
    analysis_id: Optional[int] = None
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
    event_time: Optional[datetime] = None
    event_time_precision: Optional[str] = None
    geocoding_status: str = "unresolved"
    geocoding_provider: Optional[str] = None
    geocoding_query: Optional[str] = None
    geocoding_display_name: Optional[str] = None
    geocoded_at: Optional[datetime] = None
    geocoding_error_code: Optional[str] = None
    first_seen_at: datetime = Field(default_factory=datetime.now)
    last_seen_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: EventStatus = EventStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class HealthStatus(BaseModel):
    """ヘルスチェック応答モデル"""
    status: str = "ok"
    database: str = "ok"
    llm: str = "ok"
    queue: str = "ok"
