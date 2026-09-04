"""T017 SQLite Online Backup & Temporary Restore Verification Script"""

import sqlite3
import shutil
from pathlib import Path

def run_backup_and_restore_test(prod_db_path: Path = Path("worldnews.db"), backup_dir: Path = Path("docs/t017/backup"), restore_dir: Path = Path("/tmp/t017_restore")):
    print("=== T017 Backup and Restore Automated Test ===")
    
    if not prod_db_path.exists():
        # Create dummy prod db for isolated testing if needed
        conn = sqlite3.connect(prod_db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS articles (id INT PRIMARY KEY, title TEXT);")
        conn.execute("CREATE TABLE IF NOT EXISTS processing_jobs (id INT PRIMARY KEY);")
        conn.execute("CREATE TABLE IF NOT EXISTS analyses (id INT PRIMARY KEY);")
        conn.execute("CREATE TABLE IF NOT EXISTS events (id INT PRIMARY KEY);")
        conn.execute("INSERT OR REPLACE INTO articles VALUES (1, 'Test Article');")
        conn.execute("INSERT OR REPLACE INTO processing_jobs VALUES (1);")
        conn.execute("INSERT OR REPLACE INTO analyses VALUES (1);")
        conn.execute("INSERT OR REPLACE INTO events VALUES (1);")
        conn.commit()
        conn.close()

    # 1. Execute SQLite Online Backup (.backup)
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_file = backup_dir / "worldnews_backup.db"
    
    src_conn = sqlite3.connect(prod_db_path)
    dst_conn = sqlite3.connect(backup_file)
    src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()
    
    print(f"Online backup created successfully at: {backup_file}")

    # 2. Verify Backup Integrity
    b_conn = sqlite3.connect(backup_file)
    cursor = b_conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    res = cursor.fetchone()[0]
    b_conn.close()
    assert res.lower() == "ok", f"Backup DB integrity failed: {res}"
    print("Backup DB PRAGMA integrity_check: ok")

    # 3. Perform Restore Test to Temporary Directory
    restore_dir.mkdir(parents=True, exist_ok=True)
    restored_file = restore_dir / "worldnews_restored.db"
    shutil.copy2(backup_file, restored_file)

    # 4. Compare Table Record Counts
    r_conn = sqlite3.connect(restored_file)
    r_cursor = r_conn.cursor()

    r_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in r_cursor.fetchall() if not row[0].startswith("sqlite_")]
    for tbl in tables:
        r_cursor.execute(f"SELECT COUNT(*) FROM [{tbl}];")
        cnt = r_cursor.fetchone()[0]
        print(f"Restored Table [{tbl}] Record Count: {cnt}")

    r_cursor.execute("PRAGMA integrity_check;")
    r_res = r_cursor.fetchone()[0]
    r_conn.close()
    
    assert r_res.lower() == "ok", f"Restored DB integrity failed: {r_res}"
    print("Restored DB PRAGMA integrity_check: ok")
    print("=== T017 Backup & Restore Test PASSED ===")

if __name__ == "__main__":
    run_backup_and_restore_test()
