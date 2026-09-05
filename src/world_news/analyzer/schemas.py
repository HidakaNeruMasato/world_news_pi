"""Analyzer 構造化スキーマおよびバリデーションモジュール"""

import re
from typing import Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, field_validator
from world_news.schemas import EventCategory, AnalysisErrorCode

# 代表的 ISO 3166-1 alpha-2 国コード集合
ISO_COUNTRY_CODES = {
    "AF", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ",
    "BS", "BH", "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT", "BO", "BA", "BW", "BR", "IO",
    "BG", "BF", "BI", "KH", "CM", "CA", "CV", "KY", "CF", "TD", "CL", "CN", "CX", "CC", "CO",
    "KM", "CG", "CD", "CK", "CR", "CI", "HR", "CU", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC",
    "EG", "SV", "GQ", "ER", "EE", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "GA", "GM",
    "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "GW", "GY", "HT",
    "VA", "HN", "HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP",
    "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY",
    "LI", "LT", "LU", "MO", "MK", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU",
    "YT", "MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL",
    "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MP", "NO", "OM", "PK", "PW", "PS", "PA", "PG",
    "PY", "PE", "PH", "PN", "PL", "PT", "PR", "QA", "RE", "RO", "RU", "RW", "BL", "SH", "KN",
    "LC", "MF", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SK", "SI",
    "SB", "SO", "ZA", "GS", "ES", "LK", "SD", "SR", "SJ", "SZ", "SE", "CH", "SY", "TW", "TJ",
    "TZ", "TH", "TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE",
    "GB", "US", "UM", "UY", "UZ", "VU", "VE", "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW"
}


class LLMAnalysisOutput(BaseModel):
    """LLM解析応答 Pydantic バリデーションモデル"""
    is_event: bool = Field(description="地図に掲載すべき具体的な事件か否か")
    event_type: Optional[str] = Field(default="other", description="イベントカテゴリ種別 enum")
    event_country: Optional[str] = Field(default=None, description="事件発生国 ISO2 コード")
    event_region: Optional[str] = Field(default=None, description="発生都道府県・州名")
    event_city: Optional[str] = Field(default=None, description="発生都市・市区町村名")
    location_name: Optional[str] = Field(default=None, description="具体的地名・施設名")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="自己評価信頼度")
    event_time: Optional[str] = Field(default=None, description="イベント発生日時 (ISO format)")
    event_time_precision: Optional[str] = Field(default=None, description="時間精度 (day/hour/approximate)")

    @field_validator("event_country")
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip().upper()
        if not cleaned or cleaned in ("NULL", "NONE", "UNKNOWN", "XX"):
            return None
        if len(cleaned) == 2 and cleaned in ISO_COUNTRY_CODES:
            return cleaned
        raise ValueError(f"Invalid ISO 3166-1 alpha-2 country code: {v}")

    @field_validator("event_type")
    def validate_event_type(cls, v: Optional[str]) -> str:
        if not v or not isinstance(v, str) or v.strip().lower() in ("null", "none", "unknown"):
            return EventCategory.OTHER.value
        valid_types = [e.value for e in EventCategory]
        cleaned = v.strip().lower()
        if cleaned not in valid_types:
            # 類似キー マッピング
            if "earthquake" in cleaned or "quake" in cleaned:
                return EventCategory.EARTHQUAKE.value
            if "accident" in cleaned or "collision" in cleaned:
                return EventCategory.ACCIDENT.value
            if "crime" in cleaned or "robbery" in cleaned:
                return EventCategory.CRIME.value
            if "conflict" in cleaned or "war" in cleaned:
                return EventCategory.ARMED_CONFLICT.value
            return EventCategory.OTHER.value
        return cleaned

    @field_validator("event_region", "event_city", "location_name")
    def validate_string_lengths(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned or cleaned.lower() in ("null", "none", "unknown", "n/a"):
            return None
        if len(cleaned) > 128:
            return cleaned[:128]
        return cleaned


def detect_location_hallucination(article_text: str, location_str: Optional[str]) -> bool:
    """記事本文中に抽出地名が含まれているかをチェックし、ハルシネーションの可能性を検出します。
    包含されていない場合、True (ハルシネーション疑い) を返します。
    """
    if not location_str:
        return False

    text_lower = article_text.lower()
    loc_lower = location_str.lower()

    if loc_lower in text_lower:
        return False

    # 部分一致単語のチェック
    words = [w for w in re.split(r"\W+", loc_lower) if len(w) >= 3]
    for w in words:
        if w in text_lower:
            return False

    return True
