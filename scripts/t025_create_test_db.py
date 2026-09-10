"""T025 Friend Test DB Snapshot Generator (scripts/t025_create_test_db.py)

本番 DB (worldnews.db) から安全なリードオンリースナップショット worldnews_test.db を生成します。
友人外部テスト用データセット（100〜200記事、30〜50イベント、T024多様状態）を準備します。
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

PROD_DB_PATH = "worldnews.db"
TEST_DB_PATH = "worldnews_test.db"


def create_test_db_snapshot(prod_db: str = PROD_DB_PATH, test_db: str = TEST_DB_PATH) -> dict:
    """本番 DB からリードオンリースナップショット worldnews_test.db を作成します。"""
    if not os.path.exists(prod_db):
        raise FileNotFoundError(f"Production database '{prod_db}' not found.")

    if os.path.exists(test_db):
        os.remove(test_db)

    print(f"[+] Creating Friend Test DB snapshot '{test_db}' from '{prod_db}'...", flush=True)

    src_conn = sqlite3.connect(f"file:{prod_db}?mode=ro", uri=True, timeout=30.0)
    dst_conn = sqlite3.connect(test_db, timeout=30.0)

    # 1. Copy schema & data from prod DB
    src_conn.backup(dst_conn)
    src_conn.close()

    dst_cur = dst_conn.cursor()

    # Enable WAL mode & busy timeout
    dst_cur.execute("PRAGMA journal_mode = WAL;")
    dst_cur.execute("PRAGMA busy_timeout = 30000;")

    # 2. Create metadata table
    dst_cur.execute("""
        CREATE TABLE IF NOT EXISTS test_db_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    now_str = datetime.now(timezone.utc).isoformat()
    dst_cur.execute("SELECT COUNT(*) FROM events;")
    event_count = dst_cur.fetchone()[0]

    dst_cur.execute("SELECT COUNT(*) FROM articles;")
    article_count = dst_cur.fetchone()[0]

    metadata = {
        "environment": "friend_test_readonly",
        "snapshot_timestamp": now_str,
        "event_count": str(event_count),
        "article_count": str(article_count),
    }

    for k, v in metadata.items():
        dst_cur.execute("""
            INSERT OR REPLACE INTO test_db_metadata (key, value, created_at)
            VALUES (?, ?, ?)
        """, (k, v, now_str))

    # 3. Ensure diverse T024 URL statuses exist for UX evaluation if counts are low
    dst_cur.execute("SELECT DISTINCT url_status FROM articles;")
    existing_statuses = set(row[0] for row in dst_cur.fetchall() if row[0])

    required_statuses = ["active", "redirected", "not_found", "gone", "blocked", "temporary_unavailable"]
    missing_statuses = [s for s in required_statuses if s not in existing_statuses]

    if missing_statuses:
        # Seed test sample articles with missing T024 statuses for testing
        dst_cur.execute("SELECT id, url FROM articles LIMIT 10;")
        sample_articles = dst_cur.fetchall()
        for idx, missing_s in enumerate(missing_statuses):
            if idx < len(sample_articles):
                art_id = sample_articles[idx][0]
                art_url = sample_articles[idx][1] or f"https://example.com/test-status-{missing_s}"
                link_avail = "usable" if missing_s in ("active", "redirected") else ("unavailable" if missing_s in ("not_found", "gone") else "unknown")
                dst_cur.execute("""
                    UPDATE articles
                    SET url_status = ?, link_availability = ?, url_http_status = ?
                    WHERE id = ?
                """, (missing_s, link_avail, 200 if missing_s in ("active", "redirected") else (404 if missing_s == "not_found" else 410), art_id))

                dst_cur.execute("""
                    INSERT INTO article_url_history (article_id, url, url_type, http_status, status, from_status, to_status, reason, observed_at)
                    VALUES (?, ?, 'original', ?, ?, 'unknown', ?, 't025_seed', ?)
                """, (art_id, art_url, 200 if missing_s in ("active", "redirected") else 404, missing_s, missing_s, now_str))

    dst_conn.commit()
    dst_conn.execute("PRAGMA wal_checkpoint(PASSIVE);")
    dst_conn.close()

    print(f"[+] Friend Test DB successfully created! Events: {event_count}, Articles: {article_count}", flush=True)

    return {
        "test_db_path": test_db,
        "event_count": event_count,
        "article_count": article_count,
        "snapshot_timestamp": now_str,
    }


if __name__ == "__main__":
    create_test_db_snapshot()
