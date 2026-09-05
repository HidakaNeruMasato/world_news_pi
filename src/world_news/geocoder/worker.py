"""Pi4 Geocoding バッチ/常駐ワーカー"""

import time
import logging
from typing import Optional, List, Dict, Any

from world_news.config import AppConfig, load_config
from world_news.api.database import Pi4Database
from world_news.schemas import GeocodingStatus, GeocodingErrorCode
from world_news.geocoder.base import BaseGeocoder, GeocodingResult
from world_news.geocoder.nominatim import NominatimGeocoder
from world_news.geocoder.location_resolver import LocationResolver

logger = logging.getLogger("world_news.geocoder.worker")


class EventGeocoderWorker:
    """Pi4 未解決イベント Geocoding ワーカークラス"""

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        db: Optional[Pi4Database] = None,
        geocoder: Optional[BaseGeocoder] = None,
        poll_interval_seconds: int = 10,
    ):
        self.config = config or load_config()
        self.db = db or Pi4Database(db_path=self.config.pi4.db_path)
        self.geocoder = geocoder or NominatimGeocoder()
        self.resolver = LocationResolver(geocoder=self.geocoder)
        self.poll_interval_seconds = poll_interval_seconds
        self.running = False

    def process_event(self, event_dict: dict) -> GeocodingResult:
        """単一のイベントに対して Geocoding 処理（キャッシュチェック・Resolver呼び出し・DB更新）を行います"""
        event_id = event_dict["id"]
        country = event_dict.get("country_code")
        region = event_dict.get("region")
        city = event_dict.get("city")
        location_name = event_dict.get("location_name")

        logger.info(f"Processing Geocoding for Event #{event_id} (Country: {country}, City: {city}, Loc: {location_name})")

        # 1. 候補クエリ群の生成
        queries = self.resolver.build_fallback_queries(country, region, city, location_name)

        if not queries:
            logger.info(f"Event #{event_id} has no detailed city/region. Keeping as unresolved (no_country_centroid).")
            res = GeocodingResult(
                status=GeocodingStatus.UNRESOLVED.value,
                error_code=GeocodingErrorCode.NO_COUNTRY_CENTROID.value,
                provider=self.geocoder.provider_name,
            )
            self.db.update_event_geocoding_result(
                event_id=event_id,
                geocoding_status=res.status,
                error_code=res.error_code,
                provider=res.provider,
            )
            return res

        # 2. キャッシュチェック & 段階的検索
        result = None
        for query in queries:
            cache = self.db.get_geocoding_cache(query)
            if cache:
                logger.info(f"Geocoding Cache Hit for query '{query}'")
                lat = cache["latitude"]
                lon = cache["longitude"]
                resolved_name = cache["resolved_name"]
                raw_json = cache.get("result_json", {})
                cached_country = raw_json.get("address", {}).get("country_code", "").upper() if isinstance(raw_json, dict) else None

                if lat is not None and lon is not None:
                    # 国一致チェック
                    if self.resolver.validate_country_match(country, cached_country):
                        result = GeocodingResult(
                            latitude=lat,
                            longitude=lon,
                            country_code=cached_country,
                            display_name=resolved_name,
                            raw_json=raw_json,
                            status=GeocodingStatus.RESOLVED.value,
                            error_code=GeocodingErrorCode.RESOLVED.value,
                            provider=cache["provider"],
                            query=query,
                        )
                        break

            # キャッシュにないか未ヒット ➔ Resolver 経由で Geocoder 呼び出し
            res = self.geocoder.geocode(query)

            # キャッシュへ保存
            self.db.save_geocoding_cache(
                query=query,
                provider=res.provider,
                result_json=res.raw_json or {},
                latitude=res.latitude,
                longitude=res.longitude,
                resolved_name=res.display_name,
            )

            if res.status == GeocodingStatus.RESOLVED.value:
                # 国一致および座標妥当性チェック
                if self.resolver.validate_coordinates(res.latitude, res.longitude) and \
                   self.resolver.validate_country_match(country, res.country_code):
                    result = res
                    break

        if not result:
            result = GeocodingResult(
                status=GeocodingStatus.UNRESOLVED.value,
                error_code=GeocodingErrorCode.NOT_FOUND.value,
                provider=self.geocoder.provider_name,
                query=queries[0] if queries else "",
            )

        # 3. DB 更新
        self.db.update_event_geocoding_result(
            event_id=event_id,
            geocoding_status=result.status,
            latitude=result.latitude,
            longitude=result.longitude,
            provider=result.provider,
            query=result.query,
            display_name=result.display_name,
            error_code=result.error_code,
        )

        logger.info(f"Event #{event_id} Geocoding finished: status={result.status}, lat={result.latitude}, lon={result.longitude}, err={result.error_code}")
        return result

    def process_unresolved_batch(self, limit: int = 50) -> int:
        """未解決イベントのバッチ処理を実行します"""
        events = self.db.get_unresolved_events(limit=limit)
        if not events:
            return 0

        count = 0
        for evt in events:
            # 既に解決済み/直近エラーリトライ制御などをスルー
            self.process_event(evt)
            count += 1
        return count

    def run_loop(self):
        """ワーカー常駐ループ"""
        self.running = True
        logger.info("Starting EventGeocoderWorker loop...")
        while self.running:
            try:
                processed = self.process_unresolved_batch(limit=20)
                if processed == 0:
                    time.sleep(self.poll_interval_seconds)
            except KeyboardInterrupt:
                logger.info("Worker interrupted by user.")
                break
            except Exception as e:
                logger.error(f"Error in GeocoderWorker loop: {e}", exc_info=True)
                time.sleep(self.poll_interval_seconds)
