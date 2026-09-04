# T016 Architecture — Production Quality Monitoring

```text
                 ┌───────────────────────────┐
                 │ World News QualityMonitor │
                 └─────────────┬─────────────┘
                               │
RSS Feeds ──→ Collector ──→ Pi4 Pipeline ──→ API / Web UI
    │             │              │                │
    └─────────────┴──────────────┴────────────────┘
                               │
                               ▼
                    [monitoring.db SQLite]
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
      Metrics Engine     Alert Engine     Daily Reporter
             │                 │                 │
             ▼                 ▼                 ▼
       Status / Health   Alert Rules       Daily Reports
        (CLI / API)    (OPEN/RESOLVED)    (Trend / Audit)
```

## Component Architecture
1. **QualityMonitor Engine (`src/world_news/monitoring.py`)**:
   - Collects operational metrics across all nodes (Pi3 Collector, Pi4 Pipeline, SQLite integrity, Disk/RAM, Systemd Services, API endpoints).
   - Manages heartbeat updates (`last_monitor_run`).
2. **Metrics Storage (`monitoring.db`)**:
   - Isolated SQLite database storing raw time-series metrics, alert logs, and daily aggregations.
3. **Alert Manager**:
   - Evaluates thresholds across 4 Severities (`INFO`, `WARNING`, `ERROR`, `CRITICAL`).
   - Handles deduplication, cooldown periods, and state transitions (`OPEN` -> `RESOLVED`).
4. **CLI & Health Interfaces**:
   - CLI: `python -m world_news.monitor --status / --daily / --alerts / --health`
   - API: `GET /api/health`
