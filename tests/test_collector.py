"""T003 RSS Collector 全要件対応ユニットテスト (全15テスト)"""

import gc
import tempfile
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from world_news.config import FeedConfig, AppConfig
from world_news.collector.parser import FeedParser, FeedParseError
from world_news.collector.fetcher import FeedFetcher
from world_news.collector.normalizer import ArticleNormalizer, ParsedItem
from world_news.collector.queue import CollectorQueue, QueueStatus
from world_news.collector.delivery import Pi4DeliveryClient, DeliveryResult
from world_news.collector.scheduler import CollectorScheduler
from world_news.schemas import Article


@pytest.fixture
def temp_db_path():
    """一時的 SQLite DB パスを生成するフィクスチャ"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    yield path
    gc.collect()
    if path.exists():
        try:
            path.unlink()
        except PermissionError:
            pass


# 1. RSS 2.0 parse
def test_rss2_parse():
    xml_data = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Sample RSS</title>
            <item>
                <guid>guid-123</guid>
                <title>Test Title</title>
                <description>Test Description</description>
                <link>http://example.com/item1</link>
                <pubDate>Mon, 01 Sep 2026 12:00:00 GMT</pubDate>
            </item>
        </channel>
    </rss>""".encode("utf-8")

    parser = FeedParser()
    items = parser.parse(xml_data)
    assert len(items) == 1
    assert items[0].guid == "guid-123"
    assert items[0].title == "Test Title"
    assert items[0].description == "Test Description"
    assert items[0].link == "http://example.com/item1"


# 2. Atom parse
def test_atom_parse():
    xml_data = """<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
        <title>Sample Atom Feed</title>
        <entry>
            <id>urn:uuid:atom-456</id>
            <title>Atom Entry Title</title>
            <summary>Atom Summary</summary>
            <link rel="alternate" href="http://example.com/atom1"/>
            <updated>2026-09-01T12:00:00Z</updated>
        </entry>
    </feed>""".encode("utf-8")

    parser = FeedParser()
    items = parser.parse(xml_data)
    assert len(items) == 1
    assert items[0].guid == "urn:uuid:atom-456"
    assert items[0].title == "Atom Entry Title"
    assert items[0].description == "Atom Summary"
    assert items[0].link == "http://example.com/atom1"


# 3. malformed feed
def test_malformed_feed():
    bad_xml = b"<rss><channel><title>Broken XML"
    parser = FeedParser()
    with pytest.raises(FeedParseError):
        parser.parse(bad_xml)


# 4. HTTP timeout
def test_http_timeout():
    fetcher = FeedFetcher(timeout=1)
    with patch("urllib.request.urlopen", side_effect=TimeoutError("Timeout")):
        res = fetcher.fetch("http://example.com/feed.xml")
        assert res.status_code == 0
        assert "Timeout" in res.error_message


# 5. duplicate GUID
def test_duplicate_guid(temp_db_path):
    queue = CollectorQueue(db_path=temp_db_path)
    art1 = Article(source_id=1, external_id="same-guid", title="Title 1", url="http://example.com/1")
    art2 = Article(source_id=1, external_id="same-guid", title="Title 2", url="http://example.com/2")

    id1 = queue.enqueue_article(art1)
    id2 = queue.enqueue_article(art2)
    assert id1 is not None
    assert id2 is None


# 6. duplicate URL
def test_duplicate_url(temp_db_path):
    queue = CollectorQueue(db_path=temp_db_path)
    art1 = Article(source_id=1, external_id="g1", title="Title 1", url="http://example.com/same-url")
    art2 = Article(source_id=1, external_id="g2", title="Title 2", url="http://example.com/same-url")

    id1 = queue.enqueue_article(art1)
    id2 = queue.enqueue_article(art2)
    assert id1 is not None
    assert id2 is None


# 7. duplicate content hash
def test_duplicate_content_hash(temp_db_path):
    queue = CollectorQueue(db_path=temp_db_path)
    art1 = Article(source_id=1, external_id="g1", title="Same Title", content_hash="hash-abc")
    art2 = Article(source_id=1, external_id="g2", title="Same Title", content_hash="hash-abc")

    id1 = queue.enqueue_article(art1)
    id2 = queue.enqueue_article(art2)
    assert id1 is not None
    assert id2 is None


# 8. source_country 保持
def test_source_country_preserved():
    feed = FeedConfig(id=1, name="BBC", source_country="GB", feed_url="http://example.com")
    item = ParsedItem(guid="g1", title="UK Event", description="Desc", link="http://example.com/1", published_raw=None)
    normalizer = ArticleNormalizer()
    article = normalizer.normalize(item, feed)

    assert article.source_country == "GB"


# 9. Pi4 送信成功 (ACK 受信)
def test_pi4_delivery_success(temp_db_path):
    queue = CollectorQueue(db_path=temp_db_path)
    art = Article(source_id=1, external_id="g1", title="Title", url="http://example.com/1")
    row_id = queue.enqueue_article(art)

    mock_client = MagicMock(spec=Pi4DeliveryClient)
    mock_client.deliver_batch.return_value = DeliveryResult(success_ids=[row_id], failed_items=[])

    config = AppConfig()
    config.pi3.db_path = str(temp_db_path)
    scheduler = CollectorScheduler(config=config, queue=queue, delivery_client=mock_client)

    scheduler.process_delivery()

    # sent に変更されていること
    art_after = queue.get_article_by_id(row_id)
    assert art_after["status"] == QueueStatus.SENT


# 10. Pi4 送信失敗 (pending 保持)
def test_pi4_delivery_failure(temp_db_path):
    queue = CollectorQueue(db_path=temp_db_path)
    art = Article(source_id=1, external_id="g1", title="Title", url="http://example.com/1")
    row_id = queue.enqueue_article(art)

    mock_client = MagicMock(spec=Pi4DeliveryClient)
    mock_client.deliver_batch.return_value = DeliveryResult(success_ids=[], failed_items=[(row_id, "Connection refused")])

    config = AppConfig()
    scheduler = CollectorScheduler(config=config, queue=queue, delivery_client=mock_client)

    scheduler.process_delivery()

    # 指数バックオフ待機を含む pending レコードとして保持されていること
    pending_all = queue.get_pending_articles(include_future_retries=True)
    assert len(pending_all) == 1
    assert pending_all[0]["id"] == row_id
    assert pending_all[0]["status"] == QueueStatus.PENDING
    assert pending_all[0]["retry_count"] == 1


# 11. retry (指数バックオフ)
def test_retry_backoff(temp_db_path):
    queue = CollectorQueue(db_path=temp_db_path)
    art = Article(source_id=1, external_id="g1", title="Title", url="http://example.com/1")
    row_id = queue.enqueue_article(art)

    queue.mark_failed(row_id, "Error 1", max_retries=3, initial_backoff_seconds=5)
    
    # 即時リトライ対象には含まれない（未来の時刻に設定されるため）
    pending_immediate = queue.get_pending_articles(include_future_retries=False)
    assert len(pending_immediate) == 0

    # 全体としては pending 保持されていること
    pending_all = queue.get_pending_articles(include_future_retries=True)
    assert len(pending_all) == 1
    assert pending_all[0]["retry_count"] == 1


# 12. pending queue persistence (SQLite への保存)
def test_pending_queue_persistence(temp_db_path):
    queue = CollectorQueue(db_path=temp_db_path)
    art = Article(source_id=1, external_id="g1", title="Title", url="http://example.com/1")
    row_id = queue.enqueue_article(art)

    pending = queue.get_pending_articles()
    assert len(pending) == 1
    assert pending[0]["title"] == "Title"


# 13. process restart 後の pending 復元
def test_process_restart_persistence(temp_db_path):
    q1 = CollectorQueue(db_path=temp_db_path)
    art = Article(source_id=1, external_id="g1", title="Title", url="http://example.com/1")
    q1.enqueue_article(art)

    q2 = CollectorQueue(db_path=temp_db_path)
    pending = q2.get_pending_articles()
    assert len(pending) == 1
    assert pending[0]["title"] == "Title"


# 14. ACK 前に sent へ変更されないこと
def test_no_sent_without_ack(temp_db_path):
    queue = CollectorQueue(db_path=temp_db_path)
    art = Article(source_id=1, external_id="g1", title="Title", url="http://example.com/1")
    row_id = queue.enqueue_article(art)

    queue.mark_sending([row_id])
    queue.mark_failed(row_id, "Network failure", max_retries=5, initial_backoff_seconds=5)

    art_after = queue.get_article_by_id(row_id)
    assert art_after["status"] != QueueStatus.SENT
    assert art_after["status"] == QueueStatus.PENDING


# 15. 複数フィードのうち1つが失敗しても他フィードが処理されること
def test_partial_feed_failure_isolation(temp_db_path):
    f1 = FeedConfig(id=1, name="Good Feed", source_country="JP", feed_url="http://good.example.com/rss")
    f2 = FeedConfig(id=2, name="Bad Feed", source_country="US", feed_url="http://bad.example.com/rss")

    config = AppConfig()
    config.feeds = [f1, f2]
    config.pi3.db_path = str(temp_db_path)

    xml_good = """<?xml version="1.0"?><rss version="2.0"><channel><item><guid>g1</guid><title>Good Item</title></item></channel></rss>""".encode("utf-8")

    def mock_fetch(url, timeout=20):
        if "good" in url:
            from world_news.collector.fetcher import FetchResult
            return FetchResult(content=xml_good, status_code=200)
        else:
            from world_news.collector.fetcher import FetchResult
            return FetchResult(content=None, status_code=500, error_message="Internal Error")

    queue = CollectorQueue(db_path=temp_db_path)
    scheduler = CollectorScheduler(config=config, queue=queue)
    scheduler.fetcher.fetch = MagicMock(side_effect=mock_fetch)
    
    mock_delivery = MagicMock(spec=Pi4DeliveryClient)
    mock_delivery.deliver_batch.return_value = DeliveryResult(success_ids=[], failed_items=[(1, "Mock delivery fail")])
    scheduler.delivery_client = mock_delivery

    scheduler.run_once()

    pending = queue.get_pending_articles(include_future_retries=True)
    assert len(pending) == 1
    assert pending[0]["title"] == "Good Item"
