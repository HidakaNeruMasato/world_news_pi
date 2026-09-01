"""記事正規化モジュール: ParsedItem から Article スキーマへの変換"""

import hashlib
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional
from world_news.schemas import Article, ArticleProcessingStatus
from world_news.config import FeedConfig
from world_news.collector.parser import ParsedItem


class ArticleNormalizer:
    """記事データの正規化を行うクラス"""

    @staticmethod
    def clean_html(text: Optional[str]) -> Optional[str]:
        """簡易的な HTML タグの除去"""
        if not text:
            return None
        cleaned = re.sub(r"<[^>]+>", "", text)
        return cleaned.strip() or None

    @staticmethod
    def parse_date(date_str: Optional[str]) -> datetime:
        """日時文字列のパース (RFC 822 / ISO 8601 フォールバック)"""
        if not date_str:
            return datetime.now(timezone.utc)

        # RFC 822 (pubDate)
        try:
            dt = parsedate_to_datetime(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            pass

        # ISO 8601
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            pass

        return datetime.now(timezone.utc)

    @staticmethod
    def compute_content_hash(title: str, description: Optional[str], url: Optional[str]) -> str:
        """記事タイトル、サマリー、URL から SHA256 ハッシュ値を計算"""
        raw = f"{title.strip()}|{(description or '').strip()}|{(url or '').strip()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def normalize(self, item: ParsedItem, feed: FeedConfig) -> Article:
        """ParsedItem と FeedConfig から正規化された Article を生成します"""
        title = self.clean_html(item.title) or "Untitled"
        description = self.clean_html(item.description)
        url = item.link.strip() if item.link else None
        published_at = self.parse_date(item.published_raw)
        content_hash = self.compute_content_hash(title, description, url)

        external_id = item.guid.strip() if item.guid else url

        return Article(
            source_id=feed.id,
            source_country=feed.source_country,
            external_id=external_id,
            title=title,
            description=description,
            url=url,
            published_at=published_at,
            fetched_at=datetime.now(timezone.utc),
            language=feed.language,
            content_hash=content_hash,
            processing_status=ArticleProcessingStatus.PENDING,
            retry_count=0,
        )
