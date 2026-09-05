"""Event Engine 定期実行バッチ/常駐ワーカー"""

import time
import logging
from typing import Optional

from world_news.config import AppConfig, load_config
from world_news.api.database import Pi4Database
from world_news.schemas import EventMatchingConfig
from world_news.engine.engine import EventEngine

logger = logging.getLogger("world_news.engine.worker")


class EventEngineWorker:
    """イベントエンジン常駐処理ワーカー"""

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        db: Optional[Pi4Database] = None,
        matching_config: Optional[EventMatchingConfig] = None,
        poll_interval_seconds: int = 30,
    ):
        self.config = config or load_config()
        self.db = db or Pi4Database(db_path=self.config.pi4.db_path)
        self.matching_config = matching_config or EventMatchingConfig()
        self.engine = EventEngine(
            config=self.config, db=self.db, matching_config=self.matching_config
        )
        self.poll_interval_seconds = poll_interval_seconds
        self.running = False

    def run_expiration_check(self) -> int:
        """有効期限切れイベントの非アクティブ化 (`expired`) を実行します"""
        expired_count = self.db.expire_old_events(
            lifetime_hours=self.matching_config.default_lifetime_hours
        )
        if expired_count > 0:
            logger.info(f"EventEngine: Expired {expired_count} old events.")
        return expired_count

    def run_loop(self):
        """ワーカー常駐ループ"""
        self.running = True
        logger.info("Starting EventEngineWorker loop...")
        while self.running:
            try:
                self.run_expiration_check()
                time.sleep(self.poll_interval_seconds)
            except KeyboardInterrupt:
                logger.info("Worker interrupted by user.")
                break
            except Exception as e:
                logger.error(f"Error in EventEngineWorker loop: {e}", exc_info=True)
                time.sleep(self.poll_interval_seconds)
