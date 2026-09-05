"""イベント地名の段階的 Fallback 検索および Validation リゾルバー"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from world_news.analyzer.schemas import ISO_COUNTRY_CODES
from world_news.schemas import GeocodingStatus, GeocodingErrorCode
from world_news.geocoder.base import BaseGeocoder, GeocodingResult

logger = logging.getLogger("world_news.geocoder.resolver")

# 国 ISO2 コードから英語表記へのマッピング（クエリ検索精度向上のため）
ISO_TO_COUNTRY_NAME = {
    "JP": "Japan",
    "US": "United States",
    "GB": "United Kingdom",
    "CN": "China",
    "KR": "South Korea",
    "IN": "India",
    "FR": "France",
    "DE": "Germany",
    "RU": "Russia",
    "UA": "Ukraine",
    "NP": "Nepal",
    "AF": "Afghanistan",
    "AU": "Australia",
    "CA": "Canada",
    "BR": "Brazil",
    "MX": "Mexico",
    "IT": "Italy",
    "ES": "Spain",
    "ID": "Indonesia",
    "PH": "Philippines",
    "VN": "Vietnam",
    "TH": "Thailand",
    "EG": "Egypt",
    "ZA": "South Africa",
    "IL": "Israel",
    "PS": "Palestine",
    "TR": "Turkey",
    "IR": "Iran",
    "IQ": "Iraq",
}


def get_country_name(country_code: Optional[str]) -> Optional[str]:
    if not country_code:
        return None
    code_upper = country_code.strip().upper()
    return ISO_TO_COUNTRY_NAME.get(code_upper, code_upper)


class LocationResolver:
    """イベント地名リゾルバークラス"""

    def __init__(self, geocoder: BaseGeocoder):
        self.geocoder = geocoder

    def build_fallback_queries(
        self,
        event_country: Optional[str],
        event_region: Optional[str],
        event_city: Optional[str],
        location_name: Optional[str],
    ) -> List[str]:
        """段階的 Fallback 検索クエリのリストを構築します。
        国のみのクエリ（例: 'Japan'）は、国の代表座標 (Country Centroid) 採用を防止するため除外します。
        """
        country_str = get_country_name(event_country) or ""
        region_str = event_region.strip() if event_region else ""
        city_str = event_city.strip() if event_city else ""
        loc_str = location_name.strip() if location_name else ""

        queries = []

        # 1. location_name + city + region + country
        parts1 = [p for p in [loc_str, city_str, region_str, country_str] if p]
        if len(parts1) >= 2:
            q1 = ", ".join(parts1)
            if q1 not in queries:
                queries.append(q1)

        # 2. city + region + country
        parts2 = [p for p in [city_str, region_str, country_str] if p]
        if len(parts2) >= 2:
            q2 = ", ".join(parts2)
            if q2 not in queries:
                queries.append(q2)

        # 3. city + country
        parts3 = [p for p in [city_str, country_str] if p]
        if len(parts3) >= 2:
            q3 = ", ".join(parts3)
            if q3 not in queries:
                queries.append(q3)

        # 4. region + country
        parts4 = [p for p in [region_str, country_str] if p]
        if len(parts4) >= 2:
            q4 = ", ".join(parts4)
            if q4 not in queries:
                queries.append(q4)

        return queries

    def validate_country_match(
        self, expected_country: Optional[str], geocoded_country: Optional[str]
    ) -> bool:
        """LLM の event_country と Geocoder 結果の国コードを照合・検証します。"""
        if not expected_country or not geocoded_country:
            return True  # どちらかが不明の場合は許容

        exp_upper = expected_country.strip().upper()
        geo_upper = geocoded_country.strip().upper()

        if exp_upper == "XX" or exp_upper in ("NULL", "NONE"):
            return True

        if exp_upper == geo_upper:
            return True

        # UK / GB などの別名許容
        if (exp_upper in ("GB", "UK") and geo_upper in ("GB", "UK")) or \
           (exp_upper in ("US", "USA") and geo_upper in ("US", "USA")):
            return True

        return False

    def validate_coordinates(self, lat: Optional[float], lon: Optional[float]) -> bool:
        """緯度経度の妥当性範囲 (-90..90, -180..180) をチェックします。"""
        if lat is None or lon is None:
            return False
        if not (-90.0 <= lat <= 90.0):
            return False
        if not (-180.0 <= lon <= 180.0):
            return False
        return True

    def resolve_event_location(
        self,
        event_country: Optional[str],
        event_region: Optional[str],
        event_city: Optional[str],
        location_name: Optional[str],
    ) -> GeocodingResult:
        """イベントの場所を段階的 Fallback 検索およびバリデーションを伴って解決します。"""

        # クエリが何も構成できない（国のみ含む）場合
        queries = self.build_fallback_queries(event_country, event_region, event_city, location_name)

        if not queries:
            logger.info("No detailed city/region location specified; preserving as unresolved (no_country_centroid)")
            return GeocodingResult(
                status=GeocodingStatus.UNRESOLVED.value,
                error_code=GeocodingErrorCode.NO_COUNTRY_CENTROID.value,
                provider=self.geocoder.provider_name,
                query=get_country_name(event_country) or "",
            )

        last_result = None

        for query in queries:
            logger.info(f"Trying Geocoding query: '{query}'")
            res = self.geocoder.geocode(query)
            last_result = res

            # ネットワークエラー・タイムアウト・Rate limit などの通信障害時は直ちにエラー結果を返す
            if res.error_code in (
                GeocodingErrorCode.NETWORK_ERROR.value,
                GeocodingErrorCode.TIMEOUT.value,
                GeocodingErrorCode.RATE_LIMITED.value,
            ):
                return res

            if res.status == GeocodingStatus.RESOLVED.value:
                # 1. 座標値のバリデーション
                if not self.validate_coordinates(res.latitude, res.longitude):
                    logger.warning(f"Invalid coordinates ({res.latitude}, {res.longitude}) for query '{query}'")
                    res.status = GeocodingStatus.UNRESOLVED.value
                    res.error_code = GeocodingErrorCode.INVALID_COORDINATE.value
                    res.latitude = None
                    res.longitude = None
                    continue

                # 2. 国の不一致バリデーション
                if not self.validate_country_match(event_country, res.country_code):
                    logger.warning(
                        f"Country Mismatch for query '{query}': expected '{event_country}', got '{res.country_code}'"
                    )
                    res.status = GeocodingStatus.UNRESOLVED.value
                    res.error_code = GeocodingErrorCode.COUNTRY_MISMATCH.value
                    res.latitude = None
                    res.longitude = None
                    # mismatch の場合は上位の誤った検索結果を採用しないためリトライ/fallback継続
                    continue

                # 合格
                return res

        # 全検索パターンで解決しなかった場合
        if last_result:
            return last_result

        return GeocodingResult(
            status=GeocodingStatus.UNRESOLVED.value,
            error_code=GeocodingErrorCode.NOT_FOUND.value,
            provider=self.geocoder.provider_name,
            query=queries[0] if queries else "",
        )
