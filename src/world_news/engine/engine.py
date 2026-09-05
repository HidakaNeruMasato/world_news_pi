"""Event Engine メインロジッククラス"""

import logging
from typing import Optional, Dict, Any, Tuple
from world_news.config import AppConfig, load_config
from world_news.api.database import Pi4Database
from world_news.schemas import EventMatchingConfig
from world_news.engine.matcher import is_same_event

logger = logging.getLogger("world_news.engine")


class EventEngine:
    """イベント マッチング・統合・ライフサイクル管理エンジンクラス"""

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        db: Optional[Pi4Database] = None,
        matching_config: Optional[EventMatchingConfig] = None,
    ):
        self.config = config or load_config()
        self.db = db or Pi4Database(db_path=self.config.pi4.db_path)
        self.matching_config = matching_config or EventMatchingConfig()

    def process_new_event(self, new_event_dict: dict) -> Tuple[int, bool]:
        """新規解析イベントを受け取り、既存アクティブイベントへのマージ統合または新規登録を行います。
        (event_id, is_merged) のタプルを返します。
        """
        event_type = new_event_dict.get("event_type")
        country_code = new_event_dict.get("country_code")
        article_id = new_event_dict.get("article_id")
        confidence = new_event_dict.get("confidence", 0.0)

        # 候補イベントの取得
        candidates = self.db.find_candidate_events(
            event_type=event_type, country_code=country_code
        )

        # 同一事件の検索
        matched_event = None
        for cand in candidates:
            if is_same_event(new_event_dict, cand, self.matching_config):
                matched_event = cand
                break

        if matched_event:
            # 既存イベントに統合・延命
            event_id = matched_event["id"]
            logger.info(
                f"Merging article #{article_id} into existing Event #{event_id} (Type: {event_type})"
            )
            self.db.merge_event_with_article(
                event_id=event_id,
                article_id=article_id,
                new_confidence=confidence,
                lifetime_hours=self.matching_config.default_lifetime_hours,
            )
            return event_id, True

        # マージ相手がない場合はそのまま返却
        return new_event_dict.get("id", 0), False
