# Metrics Schema & Collection Specifications

```json
{
  "day": "day-01",
  "timestamp_utc": "2026-09-05T00:00:00Z",
  "period": "24h",
  "pi3": {
    "cpu_usage_pct": 12.5,
    "ram_used_mb": 240,
    "ram_available_mb": 760,
    "disk_free_gb": 18.5,
    "articles_total": 520,
    "articles_new_24h": 520,
    "pending": 0,
    "sent": 520,
    "failed": 0
  },
  "pi4": {
    "cpu_usage_pct": 18.2,
    "ram_used_mb": 1350,
    "ram_available_mb": 2650,
    "disk_free_gb": 42.0,
    "services_status": {
      "api": "active",
      "analyzer": "active",
      "geocoder": "active",
      "engine": "active",
      "monitor": "active"
    }
  },
  "pipeline": {
    "articles_total": 520,
    "jobs_completed": 520,
    "jobs_failed": 0,
    "llm_p50_latency": 1.25,
    "llm_p95_latency": 2.10,
    "geocode_resolved": 338,
    "geocode_unresolved": 182,
    "events_created": 135,
    "events_active": 102,
    "events_merged": 18
  },
  "api_web": {
    "api_health": "HTTP 200",
    "api_active_events": "HTTP 200",
    "web_ui": "HTTP 200",
    "availability_pct": 100.0
  }
}
```
