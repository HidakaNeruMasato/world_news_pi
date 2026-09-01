"""Pi4 データベースアクセスモジュール: SQLite 7テーブルの初期化と原子性トランザクション"""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union


class Pi4Database:
    """Pi4 カノニカルデータストア (SQLite) クラス"""

    def __init__(self, db_path: Union[str, Path] = "worldnews.db"):
        self.db_path = str(db_path)
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """docs/DATABASE.md に準拠した全7テーブルおよびインデックスの初期化"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. sources
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    country_code TEXT,
                    language TEXT,
                    feed_url TEXT UNIQUE NOT NULL,
                    category TEXT,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    interval_seconds INTEGER DEFAULT 300,
                    last_success_at TEXT,
                    last_failure_at TEXT
                )
            """)

            # 2. articles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
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
                    processing_status TEXT NOT NULL DEFAULT 'pending',
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    event_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # 3. analyses
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    model_id TEXT,
                    model_version TEXT,
                    prompt_version TEXT,
                    raw_output TEXT,
                    parsed_json TEXT,
                    status TEXT,
                    error_message TEXT,
                    analyzed_at TEXT NOT NULL
                )
            """)

            # 4. events
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    country_code TEXT,
                    country_name TEXT,
                    region TEXT,
                    city TEXT,
                    location_name TEXT,
                    latitude REAL,
                    longitude REAL,
                    confidence REAL NOT NULL DEFAULT 0.0,
                    location_confidence REAL NOT NULL DEFAULT 0.0,
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # 5. article_events (中間テーブル)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS article_events (
                    article_id INTEGER NOT NULL,
                    event_id INTEGER NOT NULL,
                    relation_type TEXT,
                    similarity_score REAL,
                    PRIMARY KEY (article_id, event_id)
                )
            """)

            # 6. geocoding_cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS geocoding_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    normalized_query TEXT UNIQUE NOT NULL,
                    provider TEXT,
                    result_json TEXT,
                    latitude REAL,
                    longitude REAL,
                    resolved_name TEXT,
                    created_at TEXT NOT NULL,
                    expires_at TEXT
                )
            """)

            # 7. processing_jobs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    started_at TEXT,
                    completed_at TEXT,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT
                )
            """)

            # インデックス
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(processing_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_pubdate ON articles(published_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_hash ON articles(content_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_external_id ON articles(external_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_expires ON events(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON processing_jobs(status)")

            conn.commit()

    def find_duplicate_article(
        self,
        external_id: Optional[str],
        url: Optional[str],
        content_hash: Optional[str],
    ) -> Optional[int]:
        """重複記事が存在すればその id を返します"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if external_id:
                cursor.execute("SELECT id FROM articles WHERE external_id = ?", (external_id,))
                row = cursor.fetchone()
                if row:
                    return row["id"]

            if url:
                cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
                row = cursor.fetchone()
                if row:
                    return row["id"]

            if content_hash:
                cursor.execute("SELECT id FROM articles WHERE content_hash = ?", (content_hash,))
                row = cursor.fetchone()
                if row:
                    return row["id"]

        return None

    def insert_article_with_job(self, payload: dict) -> Tuple[int, bool]:
        """記事を受領し、articles テーブルへの追加と processing_jobs テーブルへのジョブ追加を
        単一の不可分なトランザクションとして実行します。

        Returns:
            Tuple[article_id, already_exists]
        """
        existing_id = self.find_duplicate_article(
            external_id=payload.get("external_id"),
            url=payload.get("url"),
            content_hash=payload.get("content_hash"),
        )
        if existing_id is not None:
            return existing_id, True

        now_str = datetime.now(timezone.utc).isoformat()
        fetched_at = payload.get("fetched_at") or now_str

        conn = self._get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.cursor()

            # 1. Insert Article
            cursor.execute("""
                INSERT INTO articles (
                    source_id, source_country, external_id, title, description, url,
                    published_at, fetched_at, language, content_hash, processing_status,
                    retry_count, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 0, ?, ?)
            """, (
                payload["source_id"],
                payload.get("source_country") or "XX",
                payload.get("external_id"),
                payload["title"],
                payload.get("description"),
                payload.get("url"),
                payload.get("published_at"),
                fetched_at,
                payload.get("language"),
                payload.get("content_hash"),
                now_str,
                now_str,
            ))
            article_id = cursor.lastrowid

            # 2. Insert Processing Job
            cursor.execute("""
                INSERT INTO processing_jobs (
                    article_id, job_type, status, retry_count
                ) VALUES (?, 'llm_analysis', 'pending', 0)
            """, (article_id,))

            conn.commit()
            return article_id, False

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_stats(self) -> dict:
        """各種統計データの取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM articles")
            article_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM articles WHERE processing_status = 'pending'")
            pending_articles = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM articles WHERE processing_status = 'analyzed'")
            processed_articles = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM articles WHERE processing_status = 'failed'")
            failed_articles = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM processing_jobs WHERE status = 'pending'")
            pending_jobs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM processing_jobs WHERE status = 'failed'")
            failed_jobs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM events WHERE status = 'active'")
            active_events = cursor.fetchone()[0]

            return {
                "active_events": active_events,
                "pending_articles": pending_articles,
                "processed_articles": processed_articles,
                "failed_articles": failed_articles,
                "total_articles": article_count,
                "pending_jobs": pending_jobs,
                "failed_jobs": failed_jobs,
            }
