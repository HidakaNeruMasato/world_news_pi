# Production Environment & Infrastructure Baseline

## 1. Node Topology & Roles

| Node Name | LAN IP Address | Hardware Specifications | Primary Role | Systemd Services |
|---|---|---|---|---|
| `worldnews-pi3` | `192.168.0.149` | Raspberry Pi 3 Model B (1GB RAM) | RSS Collector & Queue | `world-news-collector.service` |
| `worldnews-pi4` | `192.168.0.185` | Raspberry Pi 4 Model B (4GB RAM) | API, Analyzer, Geocoder, Engine, Web | `world-news-api`, `world-news-analyzer`, `world-news-geocoder`, `world-news-engine`, `world-news-monitor` |

---

## 2. Model & Prompts Frozen Baseline
- **LLM Model**: `Qwen2.5-1.5B-Instruct-GGUF Q4_K_M`
- **Prompt Schema**: `analysis_prompt_v2`
- **Event Threshold**: `0.35`
- **Geocoder**: `Nominatim / OpenStreetMap` (1 req/sec rate limit, SQLite cache)
- **Event Engine**: `50 km` radius, `24 hour` matching window, `6 hour` expiration
