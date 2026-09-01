"""Feed Registry モジュール: フィード設定の読み込みと状態管理"""

from typing import List, Optional
from world_news.config import AppConfig, FeedConfig


class FeedRegistry:
    """RSS/Atom フィードの登録情報を保持・管理するクラス"""

    def __init__(self, feeds: Optional[List[FeedConfig]] = None):
        self._feeds: List[FeedConfig] = feeds or []

    @classmethod
    def from_config(cls, config: AppConfig) -> "FeedRegistry":
        """AppConfig オブジェクトから FeedRegistry インスタンスを生成"""
        return cls(feeds=config.feeds)

    def get_all_feeds(self) -> List[FeedConfig]:
        """登録されているすべてのフィードを取得"""
        return self._feeds

    def get_enabled_feeds(self) -> List[FeedConfig]:
        """有効化されている (enabled=True) フィードのみを取得"""
        return [f for f in self._feeds if f.enabled]

    def get_feed_by_id(self, feed_id: int) -> Optional[FeedConfig]:
        """ID に対応するフィードを取得"""
        for f in self._feeds:
            if f.id == feed_id:
                return f
        return None
