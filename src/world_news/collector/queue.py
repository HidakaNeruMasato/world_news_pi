"""SQLite ローカル永続キューモジュール: Pi3 記事キューおよびフィード状態の永続化"""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple, Union, Dict
from world_news.schemas import Article


class QueueStatus:
    """Pi3 ローカルキュー内の記事ステータス"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"


class CollectorQueue:
    """Pi3 の SQLite ベース永続キューおよび重複判定データベースクラス"""

    def __init__(self, db_path: Union[str, Path] = "collector.db"):
        self.db_path = str(db_path)
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """テーブルおよびインデックスの初期化"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collector_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER NOT NULL,
                    source_country TEXT,
                    external_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    url TEXT,
                    published_at TEXT,
                    fetched_at TEXT NOT NULL,
                    language TEXT,
                    content_hash TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    next_retry_at TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_collector_external_id ON collector_articles(external_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_collector_url ON collector_articles(url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_collector_content_hash ON collector_articles(content_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_collector_status ON collector_articles(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_collector_title_source ON collector_articles(title, source_id)")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feed_status (
                    feed_id INTEGER PRIMARY KEY,
                    last_success_at TEXT,
                    last_failure_at TEXT,
                    last_error TEXT
                )
            """)

            conn.commit()

    def is_duplicate(
        self,
        external_id: Optional[str],
        url: Optional[str],
        content_hash: Optional[str],
        title: Optional[str] = None,
        source_id: Optional[int] = None,
        published_at: Optional[datetime] = None,
    ) -> bool:
        """重複判定ロジック"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if external_id:
                cursor.execute("SELECT id FROM collector_articles WHERE external_id = ?", (external_id,))
                if cursor.fetchone():
                    return True

            if url:
                cursor.execute("SELECT id FROM collector_articles WHERE url = ?", (url,))
                if cursor.fetchone():
                    return True

            if content_hash:
                cursor.execute("SELECT id FROM collector_articles WHERE content_hash = ?", (content_hash,))
                if cursor.fetchone():
                    return True

            if title and source_id is not None:
                cursor.execute(
                    "SELECT id FROM collector_articles WHERE title = ? AND source_id = ?",
                    (title, source_id),
                )
                if cursor.fetchone():
                    return True

        return False

    def enqueue_article(self, article: Article) -> Optional[int]:
        """記事を pending 状態として追加"""
        if self.is_duplicate(
            external_id=article.external_id,
            url=article.url,
            content_hash=article.content_hash,
            title=article.title,
            source_id=article.source_id,
            published_at=article.published_at,
        ):
            return None

        now_str = datetime.now(timezone.utc).isoformat()
        pub_str = article.published_at.isoformat() if article.published_at else now_str

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO collector_articles (
                    source_id, source_country, external_id, title, description, url,
                    published_at, fetched_at, language, content_hash, status, retry_count,
                    next_retry_at, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article.source_id,
                article.source_country,
                article.external_id,
                article.title,
                article.description,
                article.url,
                pub_str,
                article.fetched_at.isoformat(),
                article.language,
                article.content_hash,
                QueueStatus.PENDING,
                0,
                now_str,
                now_str,
                now_str,
            ))
            conn.commit()
            return cursor.lastrowid

    def get_pending_articles(self, limit: int = 50, include_future_retries: bool = False) -> List[dict]:
        """配送対象の pending 状態の記事一覧を取得"""
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if include_future_retries:
                cursor.execute("""
                    SELECT * FROM collector_articles
                    WHERE status = ?
                    ORDER BY id ASC LIMIT ?
                """, (QueueStatus.PENDING, limit))
            else:
                cursor.execute("""
                    SELECT * FROM collector_articles
                    WHERE status = ? AND (next_retry_at IS NULL OR next_retry_at <= ?)
                    ORDER BY id ASC LIMIT ?
                """, (QueueStatus.PENDING, now_str, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_article_by_id(self, article_id: int) -> Optional[dict]:
        """指定 ID の記事を取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM collector_articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def mark_sending(self, article_ids: List[int]):
        """記事のステータスを sending に変更"""
        if not article_ids:
            return
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(article_ids))
            cursor.execute(f"""
                UPDATE collector_articles
                SET status = ?, updated_at = ?
                WHERE id IN ({placeholders})
            """, [QueueStatus.SENDING, now_str] + list(article_ids))
            conn.commit()

    def mark_sent(self, article_ids: List[int]):
        """ACK 確認後に記事のステータスを sent に変更 (成功)"""
        if not article_ids:
            return
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(article_ids))
            cursor.execute(f"""
                UPDATE collector_articles
                SET status = ?, updated_at = ?
                WHERE id IN ({placeholders})
            """, [QueueStatus.SENT, now_str] + list(article_ids))
            conn.commit()

    def mark_failed(
        self,
        article_id: int,
        error_message: str,
        max_retries: int = 5,
        initial_backoff_seconds: int = 5,
    ):
        """配送失敗時の処理"""
        now = datetime.now(timezone.utc)
        now_str = now.isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT retry_count FROM collector_articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            if not row:
                return

            current_retries = row["retry_count"] + 1

            if current_retries >= max_retries:
                cursor.execute("""
                    UPDATE collector_articles
                    SET status = ?, retry_count = ?, error_message = ?, updated_at = ?
                    WHERE id = ?
                """, (QueueStatus.FAILED, current_retries, error_message, now_str, article_id))
            else:
                backoff_seconds = initial_backoff_seconds * (2 ** (current_retries - 1))
                next_retry = now + timedelta(seconds=backoff_seconds)

                cursor.execute("""
                    UPDATE collector_articles
                    SET status = ?, retry_count = ?, next_retry_at = ?, error_message = ?, updated_at = ?
                    WHERE id = ?
                """, (QueueStatus.PENDING, current_retries, next_retry.isoformat(), error_message, now_str, article_id))

            conn.commit()

    def record_feed_status(self, feed_id: int, success: bool, error_message: Optional[str] = None):
        """フィードの最新実行ステータスを記録"""
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if success:
                cursor.execute("""
                    INSERT INTO feed_status (feed_id, last_success_at, last_error)
                    VALUES (?, ?, NULL)
                    ON CONFLICT(feed_id) DO UPDATE SET
                        last_success_at = excluded.last_success_at,
                        last_error = NULL
                """, (feed_id, now_str))
            else:
                cursor.execute("""
                    INSERT INTO feed_status (feed_id, last_failure_at, last_error)
                    VALUES (?, ?, ?)
                    ON CONFLICT(feed_id) DO UPDATE SET
                        last_failure_at = excluded.last_failure_at,
                        last_error = excluded.last_error
                """, (feed_id, now_str, error_message))
            conn.commit()
