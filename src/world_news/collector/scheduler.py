"""Collector スケジューラ・メインループモジュール"""

import time
import logging
from typing import Optional
from world_news.config import AppConfig, load_config
from world_news.logging import setup_logging
from world_news.collector.feed_registry import FeedRegistry
from world_news.collector.fetcher import FeedFetcher
from world_news.collector.parser import FeedParser, FeedParseError
from world_news.collector.normalizer import ArticleNormalizer
from world_news.collector.queue import CollectorQueue
from world_news.collector.delivery import Pi4DeliveryClient


class CollectorScheduler:
    """Pi3 ニュース収集および配送メインループクラス"""

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        queue: Optional[CollectorQueue] = None,
        delivery_client: Optional[Pi4DeliveryClient] = None,
    ):
        self.config = config or load_config()
        self.registry = FeedRegistry.from_config(self.config)
        self.fetcher = FeedFetcher(timeout=10)
        self.parser = FeedParser()
        self.normalizer = ArticleNormalizer()
        self.queue = queue or CollectorQueue(db_path=self.config.pi3.db_path)
        self.delivery_client = delivery_client or Pi4DeliveryClient(
            submit_url=self.config.pi4.api_url
        )
        self.logger = logging.getLogger("world_news.collector")

    def run_once(self):
        """フィード取得・パース・DB保存および Pi4 配送を一巡実行"""
        enabled_feeds = self.registry.get_enabled_feeds()
        self.logger.info(f"Starting collector cycle for {len(enabled_feeds)} enabled feeds.")

        for feed in enabled_feeds:
            try:
                result = self.fetcher.fetch(feed.feed_url, timeout=feed.timeout_seconds)
                if result.not_modified:
                    self.logger.debug(f"Feed '{feed.name}' not modified.")
                    self.queue.record_feed_status(feed.id, success=True)
                    continue

                if result.error_message or not result.content:
                    self.logger.warning(f"Failed to fetch feed '{feed.name}': {result.error_message}")
                    self.queue.record_feed_status(feed.id, success=False, error_message=result.error_message)
                    continue

                # パース
                try:
                    items = self.parser.parse(result.content)
                except FeedParseError as e:
                    self.logger.warning(f"Parse error for feed '{feed.name}': {e}")
                    self.queue.record_feed_status(feed.id, success=False, error_message=str(e))
                    continue

                # 正規化 & 重複排除 & キュー追加
                enqueued_count = 0
                for item in items:
                    article = self.normalizer.normalize(item, feed)
                    row_id = self.queue.enqueue_article(article)
                    if row_id is not None:
                        enqueued_count += 1

                self.logger.info(f"Feed '{feed.name}': fetched {len(items)} items, enqueued {enqueued_count} new articles.")
                self.queue.record_feed_status(feed.id, success=True)

            except Exception as e:
                self.logger.error(f"Unexpected error processing feed '{feed.name}': {e}")
                self.queue.record_feed_status(feed.id, success=False, error_message=str(e))

        # pending 記事の Pi4 配送処理
        self.process_delivery()

    def process_delivery(self):
        """pending 状態の記事を Pi4 へ配送"""
        pending_articles = self.queue.get_pending_articles(limit=50)
        if not pending_articles:
            return

        self.logger.info(f"Attempting to deliver {len(pending_articles)} pending articles to Pi4...")
        self.queue.mark_sending([a["id"] for a in pending_articles])

        delivery_result = self.delivery_client.deliver_batch(pending_articles)

        # ACK 成功分の反映
        if delivery_result.success_ids:
            self.queue.mark_sent(delivery_result.success_ids)
            self.logger.info(f"Successfully delivered {len(delivery_result.success_ids)} articles to Pi4 (ACK received).")

        # 失敗分の反映 (指数バックオフリトライ)
        for article_id, error_msg in delivery_result.failed_items:
            self.queue.mark_failed(
                article_id=article_id,
                error_message=error_msg,
                max_retries=self.config.pi3.max_retries,
                initial_backoff_seconds=self.config.pi3.retry_base_delay_seconds,
            )
            self.logger.warning(f"Failed to deliver article {article_id} to Pi4: {error_msg} (retained as pending/retry).")

    def start_loop(self, interval_seconds: int = 60):
        """定期実行ループ"""
        self.logger.info("Collector loop started.")
        while True:
            try:
                self.run_once()
            except Exception as e:
                self.logger.error(f"Error in main collector loop: {e}")
            time.sleep(interval_seconds)


def main():
    setup_logging()
    scheduler = CollectorScheduler()
    scheduler.start_loop()


if __name__ == "__main__":
    main()
