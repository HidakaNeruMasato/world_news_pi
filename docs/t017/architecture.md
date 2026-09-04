# T017 System Architecture & Configuration Freeze

## 1. Configuration Freeze Matrix

| Configuration Variable | Production Frozen Value | Description / Source |
|---|---|---|
| `MODEL_VERSION` | `Qwen2.5-1.5B-Instruct-GGUF Q4_K_M` | Frozen local GGUF model size and quantization |
| `PROMPT_VERSION` | `analysis_prompt_v2` | Frozen prompt schema for event classification |
| `EVENT_THRESHOLD` | `0.35` | Frozen confidence threshold for event triggering |
| `GEOCODER_PROVIDER` | `Nominatim / OpenStreetMap` | Frozen geocoding service |
| `GEOCODER_RATE_LIMIT` | `1 req/sec` | User-Agent: `WorldNewsMap/1.0 (contact@worldnewsmap.local)` |
| `EVENT_MERGE_RADIUS_KM` | `50 km` | Haversine distance threshold for event deduplication |
| `EVENT_MERGE_WINDOW_HOURS` | `24 hours` | Time window for event deduplication matching |
| `EVENT_EXPIRATION_HOURS` | `6 hours` | Inactive event expiration threshold for active map view |
| `API_PORT` | `8080` | Production FastAPI server port |

---

## 2. Component Data Durability Matrix

| Processing Stage | Storage Location | Resendable | Idempotent | Failure Behavior |
|---|---|:---:|:---:|---|
| RSS Ingestion | Pi3 SQLite Queue | Yes | Yes | Retained in Pi3 SQLite until ACK |
| HTTP Transmission | Pi3 SQLite Queue | Yes | Yes | Retried with exponential backoff |
| Article Storage | Pi4 SQLite (`worldnews.db`) | N/A | Yes | Persisted atomically in `articles` |
| LLM Job Creation | Pi4 SQLite (`processing_jobs`) | Yes | Yes | Pending job retry on failure |
| LLM Analysis | Pi4 SQLite (`analyses`) | N/A | Yes | Persisted in `analyses` table |
| Event Generation | Pi4 SQLite (`events`) | N/A | Yes | Merged or created in `events` |
| Geocoding | Pi4 Geocoder Cache / SQLite | Yes | Yes | Unresolved status on error |
