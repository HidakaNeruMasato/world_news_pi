# T019 Dashboard API Specification

This document details the 7 FastAPI REST endpoints added in T019 under `/api/dashboard/`.

---

## Endpoint List

### 1. `GET /api/dashboard/summary`
* **Query Params**: `period` (`24h` | `48h` | `7d`, default `24h`)
* **Response**:
  ```json
  {
    "period": "24h",
    "rss_sources": 34,
    "rss_items": 1520,
    "new_articles": 1240,
    "analyzed_articles": 1210,
    "event_articles": 420,
    "geocoding_resolved": 350,
    "map_events": 310,
    "map_conversion_rate": 25.0,
    "generated_at": "2026-09-05T12:00:00Z"
  }
  ```

### 2. `GET /api/dashboard/funnel`
* **Query Params**: `period` (`24h` | `48h` | `7d`)
* **Response**: Stages and percentage reduction rates.

### 3. `GET /api/dashboard/regions`
* **Query Params**: `period` (`24h` | `48h` | `7d`)
* **Response**: List of 13 regions with `rss_sources`, `new_articles`, `event_articles`, `map_events`, and `coverage_status`.

### 4. `GET /api/dashboard/countries`
* **Query Params**: `period` (`24h` | `48h` | `7d`)
* **Response**: List of countries with `map_events` grouped by `event_country`.

### 5. `GET /api/dashboard/sources`
* **Query Params**: `period` (`24h` | `48h` | `7d`)
* **Response**: Per-media source performance metrics and conversion rates.

### 6. `GET /api/dashboard/timeseries`
* **Query Params**: `period` (`24h` | `48h` | `7d`)
* **Response**: Array of time bucket data points (`timestamp`, `new_articles`, `events`, `map_events`).

### 7. `GET /api/dashboard/source-health`
* **Response**: System & subsystem health status from T016 Monitoring.
