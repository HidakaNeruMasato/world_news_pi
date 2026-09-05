"""OpenStreetMap Nominatim Geocoder プロバイダー実装"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
import logging
from typing import Optional

from world_news.schemas import GeocodingStatus, GeocodingErrorCode
from world_news.geocoder.base import BaseGeocoder, GeocodingResult

logger = logging.getLogger("world_news.geocoder.nominatim")


class NominatimGeocoder(BaseGeocoder):
    """Nominatim OpenStreetMap Geocoder 実装クラス"""

    def __init__(
        self,
        user_agent: str = "WorldNewsMap/1.0 (contact@worldnewsmap.local)",
        endpoint_url: str = "https://nominatim.openstreetmap.org/search",
        min_interval_seconds: float = 1.0,
        timeout_seconds: float = 10.0,
    ):
        self.user_agent = user_agent
        self.endpoint_url = endpoint_url
        self.min_interval_seconds = min_interval_seconds
        self.timeout_seconds = timeout_seconds
        self._last_request_time = 0.0

    @property
    def provider_name(self) -> str:
        return "nominatim"

    def _enforce_rate_limit(self):
        """1秒間隔のリクエスト制限 (Rate Limit) を遵守します"""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.min_interval_seconds:
            time.sleep(self.min_interval_seconds - elapsed)
        self._last_request_time = time.time()

    def geocode(self, query: str) -> GeocodingResult:
        if not query or not query.strip():
            return GeocodingResult(
                status=GeocodingStatus.UNRESOLVED.value,
                error_code=GeocodingErrorCode.NOT_FOUND.value,
                provider=self.provider_name,
                query=query,
            )

        clean_query = query.strip()
        params = {
            "q": clean_query,
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": 1,
        }
        url = f"{self.endpoint_url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept-Language": "en,ja",
            },
        )

        self._enforce_rate_limit()

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                if resp.status == 200:
                    body = resp.read().decode("utf-8")
                    data = json.loads(body)
                    if not data or not isinstance(data, list) or len(data) == 0:
                        return GeocodingResult(
                            status=GeocodingStatus.UNRESOLVED.value,
                            error_code=GeocodingErrorCode.NOT_FOUND.value,
                            provider=self.provider_name,
                            query=clean_query,
                        )

                    item = data[0]
                    lat_str = item.get("lat")
                    lon_str = item.get("lon")
                    display_name = item.get("display_name")
                    address = item.get("address", {})
                    country_code = address.get("country_code", "").upper()
                    country_name = address.get("country")

                    try:
                        lat = float(lat_str) if lat_str is not None else None
                        lon = float(lon_str) if lon_str is not None else None
                    except (ValueError, TypeError):
                        return GeocodingResult(
                            status=GeocodingStatus.UNRESOLVED.value,
                            error_code=GeocodingErrorCode.INVALID_COORDINATE.value,
                            provider=self.provider_name,
                            query=clean_query,
                            raw_json=item,
                        )

                    return GeocodingResult(
                        latitude=lat,
                        longitude=lon,
                        country_code=country_code if country_code else None,
                        country_name=country_name,
                        display_name=display_name,
                        raw_json=item,
                        status=GeocodingStatus.RESOLVED.value,
                        error_code=GeocodingErrorCode.RESOLVED.value,
                        provider=self.provider_name,
                        query=clean_query,
                    )
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.warning(f"Nominatim Rate Limited (429): {e}")
                return GeocodingResult(
                    status=GeocodingStatus.UNRESOLVED.value,
                    error_code=GeocodingErrorCode.RATE_LIMITED.value,
                    provider=self.provider_name,
                    query=clean_query,
                )
            logger.error(f"Nominatim HTTP Error {e.code}: {e}")
            return GeocodingResult(
                status=GeocodingStatus.UNRESOLVED.value,
                error_code=GeocodingErrorCode.NETWORK_ERROR.value,
                provider=self.provider_name,
                query=clean_query,
            )
        except urllib.error.URLError as e:
            if isinstance(e.reason, TimeoutError) or "timed out" in str(e.reason).lower():
                logger.warning(f"Nominatim Timeout: {e}")
                return GeocodingResult(
                    status=GeocodingStatus.UNRESOLVED.value,
                    error_code=GeocodingErrorCode.TIMEOUT.value,
                    provider=self.provider_name,
                    query=clean_query,
                )
            logger.error(f"Nominatim Network Error: {e}")
            return GeocodingResult(
                status=GeocodingStatus.UNRESOLVED.value,
                error_code=GeocodingErrorCode.NETWORK_ERROR.value,
                provider=self.provider_name,
                query=clean_query,
            )
        except Exception as e:
            logger.error(f"Unexpected error in Nominatim geocode: {e}")
            return GeocodingResult(
                status=GeocodingStatus.UNRESOLVED.value,
                error_code=GeocodingErrorCode.NETWORK_ERROR.value,
                provider=self.provider_name,
                query=clean_query,
            )
