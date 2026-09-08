"""Pi4 データベースアクセスモジュール: SQLite 7テーブルの初期化と原子性トランザクション"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any


class Pi4Database:
    """Pi4 カノニカルデータストア (SQLite) クラス"""

    def __init__(self, db_path: Union[str, Path] = "worldnews.db"):
        self.db_path = str(db_path)
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    def init_db(self):
        """全7テーブルおよびインデックスの初期化"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode = WAL")

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

            # 3. analyses (T006 拡張)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    model_name TEXT NOT NULL DEFAULT 'Qwen2.5-1.5B-Instruct-GGUF',
                    model_version TEXT,
                    prompt_version TEXT NOT NULL DEFAULT 'analysis_prompt_v1',
                    raw_output TEXT,
                    parsed_output TEXT,
                    is_event INTEGER NOT NULL DEFAULT 0,
                    event_type TEXT,
                    event_country TEXT,
                    event_region TEXT,
                    event_city TEXT,
                    location_name TEXT,
                    confidence REAL DEFAULT 0.0,
                    error_code TEXT,
                    inference_time_ms REAL DEFAULT 0.0,
                    analyzed_at TEXT NOT NULL
                )
            """)

            # 既存の analyses マイグレーション
            cursor.execute("PRAGMA table_info(analyses)")
            analysis_cols = [row["name"] for row in cursor.fetchall()]
            cols_to_add = [
                ("model_name", "TEXT NOT NULL DEFAULT 'Qwen2.5-1.5B-Instruct-GGUF'"),
                ("parsed_output", "TEXT"),
                ("is_event", "INTEGER NOT NULL DEFAULT 0"),
                ("event_type", "TEXT"),
                ("event_country", "TEXT"),
                ("event_region", "TEXT"),
                ("event_city", "TEXT"),
                ("location_name", "TEXT"),
                ("confidence", "REAL DEFAULT 0.0"),
                ("error_code", "TEXT"),
                ("inference_time_ms", "REAL DEFAULT 0.0"),
            ]
            for col_name, col_def in cols_to_add:
                if col_name not in analysis_cols:
                    cursor.execute(f"ALTER TABLE analyses ADD COLUMN {col_name} {col_def}")

            # 4. events (T006 拡張)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER,
                    analysis_id INTEGER,
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
                    event_time TEXT,
                    event_time_precision TEXT,
                    geocoding_status TEXT NOT NULL DEFAULT 'unresolved',
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    expires_at TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            cursor.execute("PRAGMA table_info(events)")
            event_cols = [row["name"] for row in cursor.fetchall()]
            if "geocoding_status" not in event_cols:
                cursor.execute("ALTER TABLE events ADD COLUMN geocoding_status TEXT NOT NULL DEFAULT 'unresolved'")
            if "article_id" not in event_cols:
                cursor.execute("ALTER TABLE events ADD COLUMN article_id INTEGER")
            if "analysis_id" not in event_cols:
                cursor.execute("ALTER TABLE events ADD COLUMN analysis_id INTEGER")
            if "event_time" not in event_cols:
                cursor.execute("ALTER TABLE events ADD COLUMN event_time TEXT")
            if "event_time_precision" not in event_cols:
                cursor.execute("ALTER TABLE events ADD COLUMN event_time_precision TEXT")

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

            # 7. processing_jobs (T006 拡張)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    started_at TEXT,
                    completed_at TEXT,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT,
                    error_code TEXT
                )
            """)

            cursor.execute("PRAGMA table_info(processing_jobs)")
            job_cols = [row["name"] for row in cursor.fetchall()]
            if "error_code" not in job_cols:
                cursor.execute("ALTER TABLE processing_jobs ADD COLUMN error_code TEXT")

            cursor.execute("PRAGMA table_info(events)")
            evt_cols = [row["name"] for row in cursor.fetchall()]
            for col in ["geocoding_provider", "geocoding_query", "geocoding_display_name", "geocoded_at", "geocoding_error_code"]:
                if col not in evt_cols:
                    cursor.execute(f"ALTER TABLE events ADD COLUMN {col} TEXT")

            # 8. article_url_history (T024 記事URL変更履歴)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS article_url_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    url_type TEXT NOT NULL,
                    http_status INTEGER,
                    status TEXT NOT NULL,
                    observed_at TEXT NOT NULL
                )
            """)

            # T024 articles カラムマイグレーション
            cursor.execute("PRAGMA table_info(articles)")
            art_cols = [row["name"] for row in cursor.fetchall()]
            art_cols_to_add = [
                ("original_url", "TEXT"),
                ("canonical_url", "TEXT"),
                ("current_url", "TEXT"),
                ("url_status", "TEXT NOT NULL DEFAULT 'unknown'"),
                ("url_http_status", "INTEGER"),
                ("url_last_checked_at", "TEXT"),
                ("url_last_success_at", "TEXT"),
                ("url_redirect_count", "INTEGER NOT NULL DEFAULT 0"),
                ("url_error", "TEXT"),
            ]
            for col_name, col_def in art_cols_to_add:
                if col_name not in art_cols:
                    cursor.execute(f"ALTER TABLE articles ADD COLUMN {col_name} {col_def}")

            # 既存 articles データの original_url / current_url バックフィル
            cursor.execute("UPDATE articles SET original_url = url WHERE original_url IS NULL AND url IS NOT NULL")
            cursor.execute("UPDATE articles SET current_url = url WHERE current_url IS NULL AND url IS NOT NULL")

            # インデックス
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(processing_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_pubdate ON articles(published_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_hash ON articles(content_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_external_id ON articles(external_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_url_status ON articles(url_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_article_url_history_art_id ON article_url_history(article_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_expires ON events(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON processing_jobs(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_article_id ON analyses(article_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_geocoding_status ON events(geocoding_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_geocoding_cache_query ON geocoding_cache(normalized_query)")

            conn.commit()


    def find_duplicate_article(
        self,
        external_id: Optional[str],
        url: Optional[str],
        content_hash: Optional[str],
    ) -> Optional[int]:
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

    def claim_next_job(self) -> Optional[Dict[str, Any]]:
        now_str = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT j.id as job_id, j.article_id, j.retry_count,
                       a.title, a.description, a.source_country, a.published_at
                FROM processing_jobs j
                JOIN articles a ON j.article_id = a.id
                WHERE j.status = 'pending'
                ORDER BY j.id ASC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if not row:
                conn.commit()
                return None

            job_dict = dict(row)

            cursor.execute("""
                UPDATE processing_jobs
                SET status = 'processing', started_at = ?
                WHERE id = ?
            """, (now_str, job_dict["job_id"]))

            cursor.execute("""
                UPDATE articles
                SET processing_status = 'processing', updated_at = ?
                WHERE id = ?
            """, (now_str, job_dict["article_id"]))

            conn.commit()
            return job_dict
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def save_analysis_result(
        self,
        article_id: int,
        job_id: int,
        analysis_data: dict,
    ) -> Tuple[int, Optional[int]]:
        now_dt = datetime.now(timezone.utc)
        now_str = now_dt.isoformat()

        conn = self._get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.cursor()

            parsed_json_str = json.dumps(analysis_data.get("parsed_output")) if analysis_data.get("parsed_output") else None
            is_event_int = 1 if analysis_data.get("is_event") else 0

            cursor.execute("""
                INSERT INTO analyses (
                    article_id, model_name, model_version, prompt_version, raw_output,
                    parsed_output, is_event, event_type, event_country, event_region,
                    event_city, location_name, confidence, error_code, inference_time_ms, analyzed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article_id,
                analysis_data.get("model_name", "Qwen2.5-1.5B-Instruct-GGUF"),
                analysis_data.get("model_version", "Q4_K_M"),
                analysis_data.get("prompt_version", "analysis_prompt_v1"),
                analysis_data.get("raw_output"),
                parsed_json_str,
                is_event_int,
                analysis_data.get("event_type"),
                analysis_data.get("event_country"),
                analysis_data.get("event_region"),
                analysis_data.get("event_city"),
                analysis_data.get("location_name"),
                float(analysis_data.get("confidence", 0.0)),
                analysis_data.get("error_code"),
                float(analysis_data.get("inference_time_ms", 0.0)),
                now_str,
            ))
            analysis_id = cursor.lastrowid

            event_id = None
            if is_event_int == 1 and not analysis_data.get("error_code"):
                expires_at = (now_dt + timedelta(hours=24)).isoformat()
                cursor.execute("""
                    INSERT INTO events (
                        article_id, analysis_id, event_type, country_code, region, city,
                        location_name, latitude, longitude, confidence, event_time,
                        event_time_precision, geocoding_status, first_seen_at, last_seen_at,
                        expires_at, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, 'unresolved', ?, ?, ?, 'active', ?, ?)
                """, (
                    article_id,
                    analysis_id,
                    analysis_data.get("event_type") or "other",
                    analysis_data.get("event_country"),
                    analysis_data.get("event_region"),
                    analysis_data.get("event_city"),
                    analysis_data.get("location_name"),
                    float(analysis_data.get("confidence", 0.0)),
                    analysis_data.get("event_time"),
                    analysis_data.get("event_time_precision"),
                    now_str,
                    now_str,
                    expires_at,
                    now_str,
                    now_str,
                ))
                event_id = cursor.lastrowid

                cursor.execute("""
                    INSERT OR IGNORE INTO article_events (article_id, event_id, relation_type)
                    VALUES (?, ?, 'primary')
                """, (article_id, event_id))

            cursor.execute("""
                UPDATE processing_jobs
                SET status = 'completed', completed_at = ?
                WHERE id = ?
            """, (now_str, job_id))

            cursor.execute("""
                UPDATE articles
                SET processing_status = 'analyzed', event_id = ?, updated_at = ?
                WHERE id = ?
            """, (event_id, now_str, article_id))

            conn.commit()
            return analysis_id, event_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def fail_job(self, job_id: int, article_id: int, error_code: str, error_message: str, max_retries: int = 3):
        now_str = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.cursor()

            cursor.execute("SELECT retry_count FROM processing_jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            current_retries = row["retry_count"] if row else 0
            new_retries = current_retries + 1

            if new_retries <= max_retries:
                cursor.execute("""
                    UPDATE processing_jobs
                    SET status = 'pending', retry_count = ?, error_code = ?, error_message = ?
                    WHERE id = ?
                """, (new_retries, error_code, error_message, job_id))

                cursor.execute("""
                    UPDATE articles
                    SET processing_status = 'pending', retry_count = ?, updated_at = ?
                    WHERE id = ?
                """, (new_retries, now_str, article_id))
            else:
                cursor.execute("""
                    UPDATE processing_jobs
                    SET status = 'failed', retry_count = ?, error_code = ?, error_message = ?
                    WHERE id = ?
                """, (new_retries, error_code, error_message, job_id))

                cursor.execute("""
                    UPDATE articles
                    SET processing_status = 'failed', retry_count = ?, updated_at = ?
                    WHERE id = ?
                """, (new_retries, now_str, article_id))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def recover_stale_jobs(self, timeout_minutes: int = 10) -> int:
        threshold_dt = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
        threshold_str = threshold_dt.isoformat()
        now_str = datetime.now(timezone.utc).isoformat()

        conn = self._get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, article_id FROM processing_jobs
                WHERE status = 'processing' AND started_at < ?
            """, (threshold_str,))
            stale_jobs = cursor.fetchall()

            count = len(stale_jobs)
            for job in stale_jobs:
                cursor.execute("""
                    UPDATE processing_jobs
                    SET status = 'pending', error_code = 'stale_recovery', error_message = 'Job recovered from stale processing state'
                    WHERE id = ?
                """, (job["id"],))

                cursor.execute("""
                    UPDATE articles
                    SET processing_status = 'pending', updated_at = ?
                    WHERE id = ?
                """, (now_str, job["article_id"]))

            conn.commit()
            return count
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_stats(self) -> dict:
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

            cursor.execute("SELECT COUNT(*) FROM processing_jobs WHERE status = 'processing'")
            processing_jobs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM processing_jobs WHERE status = 'completed'")
            completed_jobs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM processing_jobs WHERE status = 'failed'")
            failed_jobs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM events WHERE status = 'active'")
            active_events = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM events WHERE geocoding_status = 'unresolved'")
            unresolved_events = cursor.fetchone()[0]

            return {
                "active_events": active_events,
                "unresolved_events": unresolved_events,
                "pending_articles": pending_articles,
                "processed_articles": processed_articles,
                "failed_articles": failed_articles,
                "total_articles": article_count,
                "pending_jobs": pending_jobs,
                "processing_jobs": processing_jobs,
                "completed_jobs": completed_jobs,
                "failed_jobs": failed_jobs,
            }

    def get_geocoding_cache(self, query: str) -> Optional[dict]:
        """クエリを正規化し、geocoding_cache からキャッシュ結果を取得します"""
        norm_query = query.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT provider, result_json, latitude, longitude, resolved_name, created_at
                FROM geocoding_cache
                WHERE normalized_query = ?
            """, (norm_query,))
            row = cursor.fetchone()
            if row:
                res_dict = json.loads(row["result_json"]) if row["result_json"] else {}
                return {
                    "provider": row["provider"],
                    "result_json": res_dict,
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "resolved_name": row["resolved_name"],
                    "created_at": row["created_at"],
                }
        return None

    def save_geocoding_cache(
        self,
        query: str,
        provider: str,
        result_json: dict,
        latitude: Optional[float],
        longitude: Optional[float],
        resolved_name: Optional[str],
    ):
        """geocoding_cache テーブルに検索結果を保存・更新します"""
        norm_query = query.strip().lower()
        now_str = datetime.now(timezone.utc).isoformat()
        res_json_str = json.dumps(result_json, ensure_ascii=False)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO geocoding_cache (normalized_query, provider, result_json, latitude, longitude, resolved_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(normalized_query) DO UPDATE SET
                    provider = excluded.provider,
                    result_json = excluded.result_json,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    resolved_name = excluded.resolved_name,
                    created_at = excluded.created_at
            """, (norm_query, provider, res_json_str, latitude, longitude, resolved_name, now_str))
            conn.commit()

    def get_unresolved_events(self, limit: int = 50) -> List[dict]:
        """geocoding_status = 'unresolved' のイベントを取得します"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, article_id, analysis_id, event_type, country_code, country_name, region, city, location_name,
                       latitude, longitude, geocoding_status, geocoding_provider, geocoding_query, geocoding_error_code
                FROM events
                WHERE geocoding_status = 'unresolved'
                ORDER BY id ASC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def update_event_geocoding_result(
        self,
        event_id: int,
        geocoding_status: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        provider: Optional[str] = None,
        query: Optional[str] = None,
        display_name: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        """Geocoding 実行結果を events テーブルへ更新します"""
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE events
                SET geocoding_status = ?,
                    latitude = ?,
                    longitude = ?,
                    geocoding_provider = ?,
                    geocoding_query = ?,
                    geocoding_display_name = ?,
                    geocoded_at = ?,
                    geocoding_error_code = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                geocoding_status,
                latitude,
                longitude,
                provider,
                query,
                display_name,
                now_str,
                error_code,
                now_str,
                event_id,
            ))
            conn.commit()

    def find_candidate_events(
        self, event_type: str, country_code: Optional[str] = None
    ) -> List[dict]:
        """照合候補となるアクティブなイベント一覧を取得します"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT id, article_id, analysis_id, event_type, country_code, country_name, region, city, location_name,
                       latitude, longitude, confidence, location_confidence, event_time, geocoding_status,
                       first_seen_at, last_seen_at, expires_at, status
                FROM events
                WHERE status = 'active' AND event_type = ?
            """
            params = [event_type]
            if country_code:
                query += " AND country_code = ?"
                params.append(country_code)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_event_articles(self, event_id: int) -> List[dict]:
        """指定したイベントに関連付けられたニュース記事一覧を取得します (T024 拡張)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, a.source_id, a.source_country, a.title, a.description,
                       COALESCE(a.current_url, a.url) AS url,
                       COALESCE(a.original_url, a.url) AS original_url,
                       a.canonical_url,
                       COALESCE(a.current_url, a.url) AS current_url,
                       COALESCE(a.url_status, 'unknown') AS url_status,
                       a.url_http_status, a.url_last_checked_at,
                       a.published_at, a.fetched_at, a.language, s.name as source_name
                FROM articles a
                JOIN article_events ae ON a.id = ae.article_id
                LEFT JOIN sources s ON a.source_id = s.id
                WHERE ae.event_id = ?
                ORDER BY a.published_at DESC
            """, (event_id,))
            rows = cursor.fetchall()
            if not rows:
                # 予備: articles.event_id での直接照合
                cursor.execute("""
                    SELECT a.id, a.source_id, a.source_country, a.title, a.description,
                           COALESCE(a.current_url, a.url) AS url,
                           COALESCE(a.original_url, a.url) AS original_url,
                           a.canonical_url,
                           COALESCE(a.current_url, a.url) AS current_url,
                           COALESCE(a.url_status, 'unknown') AS url_status,
                           a.url_http_status, a.url_last_checked_at,
                           a.published_at, a.fetched_at, a.language, s.name as source_name
                    FROM articles a
                    LEFT JOIN sources s ON a.source_id = s.id
                    WHERE a.event_id = ?
                    ORDER BY a.published_at DESC
                """, (event_id,))
                rows = cursor.fetchall()

            results = []
            for r in rows:
                d = dict(r)
                status = d.get('url_status', 'unknown')
                d['link_available'] = status in ('active', 'redirected', 'unknown')
                results.append(d)
            return results

    def update_article_url_status(
        self,
        article_id: int,
        original_url: str,
        current_url: str,
        canonical_url: Optional[str],
        status: str,
        http_status: Optional[int] = None,
        redirect_count: int = 0,
        error: Optional[str] = None,
    ):
        """記事の URL 検証結果および変更履歴をアトミックに記録します (T024)"""
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 既存レコード取得
            cursor.execute("SELECT current_url, url_status FROM articles WHERE id = ?", (article_id,))
            old_row = cursor.fetchone()
            old_url = old_row["current_url"] if old_row else original_url

            # articles テーブル更新
            success_clause = ", url_last_success_at = ?" if status in ('active', 'redirected') else ""
            params = [original_url, current_url, canonical_url, status, http_status, now_str, redirect_count, error]
            if status in ('active', 'redirected'):
                params.append(now_str)
            params.append(article_id)

            cursor.execute(f"""
                UPDATE articles
                SET original_url = ?,
                    current_url = ?,
                    canonical_url = ?,
                    url_status = ?,
                    url_http_status = ?,
                    url_last_checked_at = ?
                    {success_clause},
                    url_redirect_count = ?,
                    url_error = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                original_url, current_url, canonical_url, status, http_status, now_str,
                *( [now_str] if status in ('active', 'redirected') else [] ),
                redirect_count, error, now_str, article_id
            ))

            # URL に変更があった場合、履歴テーブルへ記録
            if old_url != current_url or status in ('redirected', 'not_found', 'gone'):
                cursor.execute("""
                    INSERT INTO article_url_history (article_id, url, url_type, http_status, status, observed_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    article_id,
                    current_url,
                    'redirect' if status == 'redirected' else ('canonical' if canonical_url == current_url else 'original'),
                    http_status,
                    status,
                    now_str,
                ))

            conn.commit()

    def get_article_url_history(self, article_id: int) -> List[dict]:
        """指定記事の URL 状態変更履歴を取得します (T024)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, article_id, url, url_type, http_status, status, observed_at
                FROM article_url_history
                WHERE article_id = ?
                ORDER BY id ASC
            """, (article_id,))
            return [dict(r) for r in cursor.fetchall()]


    def merge_event_with_article(
        self,
        event_id: int,
        article_id: int,
        new_confidence: float = 0.0,
        lifetime_hours: float = 6.0,
    ):
        """同一事件の新しい記事を統合し、last_seen_at および expires_at を延命・コミットします"""
        now_dt = datetime.now(timezone.utc)
        now_str = now_dt.isoformat()
        exp_dt = now_dt + timedelta(hours=lifetime_hours)
        exp_str = exp_dt.isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 既存信頼度を取得して高い方を採用
            cursor.execute("SELECT confidence FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            curr_conf = row["confidence"] if row else 0.0
            updated_conf = max(curr_conf, new_confidence)

            # 1. events 更新
            cursor.execute("""
                UPDATE events
                SET last_seen_at = ?,
                    expires_at = ?,
                    confidence = ?,
                    updated_at = ?
                WHERE id = ?
            """, (now_str, exp_str, updated_conf, now_str, event_id))

            # 2. article_events 関連追加
            cursor.execute("""
                INSERT OR IGNORE INTO article_events (article_id, event_id, relation_type)
                VALUES (?, ?, 'merged')
            """, (article_id, event_id))

            conn.commit()

    def expire_old_events(self, lifetime_hours: float = 6.0) -> int:
        """last_seen_at から指定時間が経過したイベントの status を 'expired' へ変更します"""
        now_dt = datetime.now(timezone.utc)
        now_str = now_dt.isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, last_seen_at, expires_at FROM events
                WHERE status = 'active'
            """)
            rows = cursor.fetchall()

            expired_ids = []
            for r in rows:
                last_seen = r["last_seen_at"]
                expires_at = r["expires_at"]

                # expires_at がある場合は優先チェック、無ければ last_seen_at + lifetime_hours で計算
                is_expired = False
                if expires_at:
                    try:
                        exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                        if exp_dt < now_dt:
                            is_expired = True
                    except Exception:
                        pass
                else:
                    try:
                        ls_dt = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
                        if ls_dt + timedelta(hours=lifetime_hours) < now_dt:
                            is_expired = True
                    except Exception:
                        pass

                if is_expired:
                    expired_ids.append(r["id"])

            if expired_ids:
                placeholders = ",".join("?" * len(expired_ids))
                cursor.execute(f"""
                    UPDATE events
                    SET status = 'expired', updated_at = ?
                    WHERE id IN ({placeholders})
                """, [now_str] + expired_ids)
                conn.commit()

            return len(expired_ids)

    def get_active_events(
        self, min_confidence: float = 0.50, limit: int = 100
    ) -> List[dict]:
        """地図プロット用のアクティブなイベント一覧を取得します"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, article_id, analysis_id, event_type, country_code, country_name, region, city, location_name,
                       latitude, longitude, confidence, location_confidence, event_time, geocoding_status,
                       geocoding_provider, geocoding_query, geocoding_display_name, first_seen_at, last_seen_at, expires_at, status
                FROM events
                WHERE status = 'active'
                  AND geocoding_status = 'resolved'
                  AND latitude IS NOT NULL
                  AND longitude IS NOT NULL
                  AND confidence >= ?
                ORDER BY last_seen_at DESC
                LIMIT ?
            """, (min_confidence, limit))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
