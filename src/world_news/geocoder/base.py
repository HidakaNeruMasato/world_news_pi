"""Geocoder 抽象インターフェースおよび GeocodingResult モデル"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from world_news.schemas import GeocodingStatus, GeocodingErrorCode


@dataclass
class GeocodingResult:
    """Geocoding 実行結果オブジェクト"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_code: Optional[str] = None  # ISO 3166-1 alpha-2 上文字 (例: "JP", "US")
    country_name: Optional[str] = None
    display_name: Optional[str] = None
    raw_json: Optional[Dict[str, Any]] = None
    status: str = GeocodingStatus.UNRESOLVED.value
    error_code: Optional[str] = None
    provider: str = "unknown"
    query: str = ""


class BaseGeocoder(ABC):
    """Geocoding サービスの抽象基底インターフェース"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """プロバイダー識別子名 (例: 'nominatim', 'mapbox', 'google')"""
        pass

    @abstractmethod
    def geocode(self, query: str) -> GeocodingResult:
        """指定クエリ文字列に対する Geocoding 検索を実行します"""
        pass
