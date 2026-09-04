# T016 Monitoring SQLite Database Schema (`monitoring.db`)

## 1. `metric_samples` Table
Stores raw time-series metrics.
```sql
CREATE TABLE IF NOT EXISTS metric_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    host TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    status TEXT NOT NULL,
    metadata_json TEXT
);
```

## 2. `alerts` Table
Stores active and historical alerts.
```sql
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_key TEXT UNIQUE NOT NULL,
    severity TEXT NOT NULL,
    component TEXT NOT NULL,
    message TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL -- 'OPEN' or 'RESOLVED'
);
```

## 3. `daily_summaries` Table
Stores daily aggregated operational statistics.
```sql
CREATE TABLE IF NOT EXISTS daily_summaries (
    date TEXT PRIMARY KEY,
    articles_processed INTEGER,
    events_created INTEGER,
    event_rate REAL,
    map_displayable INTEGER,
    map_display_rate REAL,
    geocoding_resolution_rate REAL,
    llm_requests INTEGER,
    llm_errors INTEGER,
    llm_p95_latency REAL,
    max_queue_backlog INTEGER,
    alerts_triggered INTEGER,
    system_status TEXT
);
```
