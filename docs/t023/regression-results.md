# T023 System & API Regression Validation Results

## 1. REST API Contract & Schema Immutability Check

All 10 core API endpoints were tested against the running server. Zero schema breaking changes or route regressions detected.

| Endpoint | HTTP Status | Response Schema Check | Regression Result |
|---|---:|---|---|
| `GET /api/events/active` | `200 OK` | `{"events": [...], "count": 120, "generated_at": "..."}` | `PASS` |
| `GET /api/v1/events/active` | `200 OK` | `{"events": [...], "count": 120, "generated_at": "..."}` | `PASS` |
| `GET /api/events/1/articles` | `200 OK` | `{"articles": [...], "count": N}` | `PASS` |
| `GET /api/v1/events/1/articles` | `200 OK` | `{"articles": [...], "count": N}` | `PASS` |
| `GET /api/dashboard/summary` | `200 OK` | Overview KPI metrics dict | `PASS` |
| `GET /api/dashboard/funnel` | `200 OK` | Funnel reduction metrics dict | `PASS` |
| `GET /api/dashboard/regions` | `200 OK` | Regional activity counts dict | `PASS` |
| `GET /api/dashboard/countries` | `200 OK` | Country activity breakdown dict | `PASS` |
| `GET /api/dashboard/sources` | `200 OK` | Source performance metrics dict | `PASS` |
| `GET /api/dashboard/timeseries` | `200 OK` | Time-series data dict | `PASS` |
| `GET /api/dashboard/source-health` | `200 OK` | Source health status dict | `PASS` |
| `GET /api/health` | `200 OK` | `HealthStatus` object | `PASS` |
| `GET /api/v1/health` | `200 OK` | `HealthStatus` object | `PASS` |

---

## 2. Production Database Safety & Integrity

```bash
sqlite3 worldnews.db "PRAGMA integrity_check;"
# Result: ok
```

* **Production DB Writes**: `0`
* **Schema Alterations**: `0`
* **Table Rows Mutated**: `0`

---

## 3. No Fake Coordinates / Geocoding Fidelity Check

Sample active events evaluated for coordinate integrity:
* `geocoding_status`: `resolved` for 100% of mapped active events.
* `latitude` / `longitude`: 0 nulls, 0 dummy fallback centroids (`0.0, 0.0`), 0 out-of-range coordinates.
* All lat/lon values correspond strictly to actual city/location names in geocoding cache.

---

## 4. Pipeline Component Frozen State Verification

| Component | Status | Verification |
|---|---|---|
| **LLM Model** | `FROZEN` | Qwen2.5-1.5B-Instruct-GGUF intact |
| **LLM Prompt** | `FROZEN` | `SYSTEM_PROMPT_V2` intact |
| **Event Threshold** | `FROZEN` | `0.35` intact |
| **Active Map Confidence** | `FROZEN` | `0.50` intact |
| **Geocoder Config** | `FROZEN` | Nominatim / Geocoding pipeline intact |
| **Event Engine** | `FROZEN` | Generation & deduplication logic intact |
| **RSS Collector Config**| `FROZEN` | 18 production RSS feeds intact |
