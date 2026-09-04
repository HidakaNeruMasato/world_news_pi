# Phase 0 — Deployment & System Inventory Audit Report

## 1. Systemd Services Inventory (Expected vs Actual)

| Service Name | Expected Status | Pi3 (192.168.0.149) | Pi4 (192.168.0.185) | Audit Status |
|---|---|---|---|:---:|
| `world-news-collector.service` | enabled / running | PASS (active) | N/A | PASS |
| `world-news-api.service` | enabled / running | N/A | PASS (active) | PASS |
| `world-news-analyzer.service` | enabled / running | N/A | PASS (active) | PASS |
| `world-news-geocoder.service` | enabled / running | N/A | PASS (active) | PASS |
| `world-news-engine.service` | enabled / running | N/A | PASS (active) | PASS |
| `world-news-monitor.service` | enabled / running | N/A | PASS (active) | PASS |

---

## 2. Infrastructure & Environment Audit

| Audit Property | Expected Value | Pi3 Actual Value | Pi4 Actual Value | Status |
|---|---|---|---|:---:|
| Hardware Host | Raspberry Pi | Pi 3 Model B (1GB RAM) | Pi 4 Model B (4GB RAM) | PASS |
| Operating System | Debian GNU/Linux | Debian 13 (trixie) | Debian 13 (trixie) | PASS |
| Python Environment | Python 3.13.x venv | `/home/hidakamasato/world_news/venv` | `/home/hidakamasato/world_news/venv` | PASS |
| Database Location | SQLite DB | `/home/hidakamasato/world_news/worldnews.db` | `/home/hidakamasato/world_news/worldnews.db` | PASS |
| Monitoring DB | SQLite DB | N/A | `/home/hidakamasato/world_news/monitoring.db` | PASS |
| LLM Model Path | GGUF Q4_K_M | N/A | `/home/hidakamasato/world_news/models/Qwen2.5-1.5B-Instruct-GGUF` | PASS |
| File Permissions | Non-root User | `hidakamasato:hidakamasato` | `hidakamasato:hidakamasato` | PASS |
| Firewall / Ports | LAN Only (8080) | Port 8080 CLOSED | Port 8080 OPEN (LAN Only) | PASS |
