"""T005 LLM ベンチマーク構造定義モジュール"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class EventTypeEnum(str, Enum):
    EARTHQUAKE = "earthquake"
    ACCIDENT = "accident"
    CRIME = "crime"
    CONFLICT = "conflict"
    POLITICS = "politics"
    ECONOMY = "economy"
    SPORTS = "sports"
    OTHER = "other"


class LLMEventOutput(BaseModel):
    """LLM に要求する構造化出力スキーマ"""
    is_event: bool = Field(description="地図上に掲載すべき明確な現場イベントか否か")
    event_type: str = Field(description="イベント種別 enum")
    event_country: Optional[str] = Field(default=None, description="事件・出来事の発生国 ISO2 コード (例: JP, US, GB, FR)")
    event_region: Optional[str] = Field(default=None, description="発生都道府県・州名")
    event_city: Optional[str] = Field(default=None, description="発生都市・市区町村名")
    location_name: Optional[str] = Field(default=None, description="具体的施設・地名")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="モデルの自己信頼度スコア")

    @field_validator("event_country")
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v.strip()) == 2:
            return v.strip().upper()
        return v


class GroundTruthItem(BaseModel):
    """Ground Truth 正解ラベルモデル"""
    id: int
    source_id: int
    source_country: str
    title: str
    description: Optional[str] = None
    expected_is_event: bool
    expected_event_type: str
    expected_event_country: Optional[str] = None
    expected_event_region: Optional[str] = None
    expected_event_city: Optional[str] = None
    case_category: Optional[str] = None


class ArticleBenchmarkMetric(BaseModel):
    """単一記事の測定結果"""
    article_id: int
    latency_ms: float
    tokens_per_sec: Optional[float] = None
    raw_output: str
    parsed_json: Optional[Dict[str, Any]] = None
    valid_json: bool
    schema_valid: bool
    enum_valid: bool
    is_event_correct: Optional[bool] = None
    country_correct: Optional[bool] = None
    location_correct: Optional[bool] = None
    ram_usage_mb: Optional[float] = None


class ModelBenchmarkSummary(BaseModel):
    """モデル全体のベンチマーク要約結果"""
    model_name: str
    file_name: str
    quantization: str
    model_size_mb: float
    license_type: str
    timestamp: str
    hardware: str = "Raspberry Pi 4 Model B (4GB RAM, Cortex-A72 ARM64)"
    threads: int = 4
    context_size: int = 2048
    temperature: float = 0.1
    total_articles: int
    load_time_ms: float
    ram_idle_mb: float
    ram_peak_mb: float
    ram_post_mb: float
    latencies_ms: List[float]
    min_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    max_latency_ms: float
    avg_tokens_per_sec: float
    valid_json_rate: float
    schema_valid_rate: float
    is_event_accuracy: float
    country_accuracy: float
    location_accuracy: float
    oom_occurred: bool = False
    details: List[ArticleBenchmarkMetric] = Field(default_factory=list)
