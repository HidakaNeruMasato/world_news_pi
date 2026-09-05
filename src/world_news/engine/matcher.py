"""イベント照合・距離計算モジュール (Haversine Formula & Matching rules)"""

import math
from datetime import datetime
from typing import Dict, Any, Optional
from world_news.schemas import EventMatchingConfig


def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """2地点の緯度経度から球面大円距離 (km) を Haversine 公式で計算します"""
    R = 6371.0  # 地球の半径 (km)

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c


def parse_iso_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def is_same_event(
    evt1: Dict[str, Any],
    evt2: Dict[str, Any],
    config: Optional[EventMatchingConfig] = None,
) -> bool:
    """2つのイベントが同一のリアルワールド事件かを多角的に判定します"""
    cfg = config or EventMatchingConfig()

    # 1. カテゴリ一致
    type1 = str(evt1.get("event_type", "")).lower()
    type2 = str(evt2.get("event_type", "")).lower()
    if type1 != type2:
        # カテゴリ不一致
        return False

    # 2. 国コード一致
    c1 = evt1.get("country_code")
    c2 = evt2.get("country_code")
    if c1 and c2 and c1.upper() != c2.upper():
        return False

    # 3. 時間差判定
    t1 = parse_iso_datetime(evt1.get("first_seen_at") or evt1.get("event_time"))
    t2 = parse_iso_datetime(evt2.get("first_seen_at") or evt2.get("event_time"))
    if t1 and t2:
        diff_hours = abs((t1 - t2).total_seconds()) / 3600.0
        if diff_hours > cfg.max_time_diff_hours:
            return False

    # 4. 座標ありの場合: 距離判定
    lat1, lon1 = evt1.get("latitude"), evt1.get("longitude")
    lat2, lon2 = evt2.get("latitude"), evt2.get("longitude")

    if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
        dist_km = calculate_haversine_distance(lat1, lon1, lat2, lon2)
        if dist_km <= cfg.max_distance_km:
            return True
        return False

    # 5. 座標なしの場合: 都市名・地名テキストの一致
    city1 = evt1.get("city")
    city2 = evt2.get("city")
    if city1 and city2 and city1.strip().lower() == city2.strip().lower():
        return True

    loc1 = evt1.get("location_name")
    loc2 = evt2.get("location_name")
    if loc1 and loc2 and loc1.strip().lower() == loc2.strip().lower():
        return True

    return False
