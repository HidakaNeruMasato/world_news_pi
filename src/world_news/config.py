"""設定ファイル読み込みモジュール"""

import os
from pathlib import Path
from typing import List, Optional
import yaml
from pydantic import BaseModel, Field


class FeedConfig(BaseModel):
    id: int
    name: str
    source_country: str = "XX"
    language: str = "en"
    feed_url: str
    category: str = "general"
    enabled: bool = True
    interval_seconds: int = 300
    timeout_seconds: int = 10


class Pi3Config(BaseModel):
    db_path: str = "collector.db"
    poll_interval_seconds: int = 300
    max_retries: int = 5
    retry_base_delay_seconds: int = 5


class Pi4Config(BaseModel):
    db_path: str = "worldnews.db"
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_url: str = "http://192.168.0.185:8080/api/v1/internal/articles"


class NodeConfig(BaseModel):
    role: str = "collector"


class AppConfig(BaseModel):
    node: NodeConfig = Field(default_factory=NodeConfig)
    pi3: Pi3Config = Field(default_factory=Pi3Config)
    pi4: Pi4Config = Field(default_factory=Pi4Config)
    feeds: List[FeedConfig] = Field(default_factory=list)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """設定 YAML ファイルを読み込み AppConfig オブジェクトを返します"""
    if config_path is None:
        # デフォルト探索パス
        candidates = [
            Path("config.yaml"),
            Path("config.example.yaml"),
            Path(__file__).parents[2] / "config.example.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                config_path = str(candidate)
                break

    if not config_path or not os.path.exists(config_path):
        return AppConfig()

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return AppConfig(**data)
