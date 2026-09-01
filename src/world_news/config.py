"""設定ファイル (YAML) の読み込みおよび構造化モデル"""

from pathlib import Path
from typing import Union, Optional, List
import yaml
from pydantic import BaseModel, Field


class SystemConfig(BaseModel):
    """システム全体設定"""
    timezone: str = "Asia/Tokyo"
    event_lifetime_hours: int = 6
    min_display_confidence: float = 0.75


class Pi3Config(BaseModel):
    """Pi3 (収集ノード) 設定"""
    host: str = "worldnews-pi3"
    submit_url: str = "http://worldnews-pi4:8080/api/v1/internal/articles"
    db_path: str = "collector.db"
    delivery_max_retries: int = 5
    delivery_initial_backoff_seconds: int = 5


class Pi4Config(BaseModel):
    """Pi4 (解析・APIノード) 設定"""
    host: str = "worldnews-pi4"
    api_port: int = 8080


class LLMConfig(BaseModel):
    """LLM 設定"""
    provider: str = "llama_cpp"
    model_id: str = "REPLACE_AFTER_BENCHMARK"
    prompt_version: str = "v1"
    temperature: float = 0.0
    max_input_chars: int = 8000
    max_output_tokens: int = 512


class GeocoderConfig(BaseModel):
    """ジオコーダー設定"""
    provider: str = "REPLACE_AFTER_PROVIDER_SELECTION"
    enabled: bool = True


class RSSConfig(BaseModel):
    """RSS設定"""
    default_interval_seconds: int = 300
    request_timeout_seconds: int = 20


class FeedConfig(BaseModel):
    """個別RSS/Atomフィード設定"""
    id: int
    name: str
    source_country: str = "XX"
    language: str = "en"
    feed_url: str
    category: Optional[str] = "general"
    enabled: bool = True
    interval_seconds: int = 300
    timeout_seconds: int = 20


class AppConfig(BaseModel):
    """アプリケーション統合設定"""
    system: SystemConfig = Field(default_factory=SystemConfig)
    pi3: Pi3Config = Field(default_factory=Pi3Config)
    pi4: Pi4Config = Field(default_factory=Pi4Config)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    geocoder: GeocoderConfig = Field(default_factory=GeocoderConfig)
    rss: RSSConfig = Field(default_factory=RSSConfig)
    feeds: List[FeedConfig] = Field(default_factory=list)


def load_config(config_path: Union[str, Path] = "config.yaml") -> AppConfig:
    """指定されたYAML設定ファイルを読み込んで AppConfig オブジェクトを返します。
    ファイルが存在しない場合は、デフォルト設定を返します。
    """
    path = Path(config_path)
    if not path.is_file():
        # config.yaml が存在しない場合は config.example.yaml も確認
        example_path = path.parent / "config.example.yaml"
        if example_path.is_file():
            path = example_path
        else:
            return AppConfig()

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return AppConfig(**data)
