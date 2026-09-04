# Production Readiness Checklist & Acceptance Criteria

| ID | Category | Requirement Description | Test Method | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|:---:|
| A-1 | Deployment | Pi3/Pi4 Systemd Services Autostart | `systemctl status` | `enabled / active` | `enabled / active` | PASS |
| B-1 | Availability | API Endpoint `/api/health` Availability | HTTP GET | HTTP 200 `status=ok` | HTTP 200 `status=ok` | PASS |
| B-2 | Availability | Web Map UI (`:8080`) Availability | HTTP GET | HTTP 200 Map Loads | HTTP 200 Map Loads | PASS |
| C-1 | Recovery | Pi3 Host Reboot Autostart & Resend | Node Reboot | 0 Data Loss | 0 Data Loss | PASS |
| C-2 | Recovery | Pi4 Host Reboot Autostart | Node Reboot | 0 Data Loss | 0 Data Loss | PASS |
| C-3 | Recovery | Network Outage Retry & ACK | Network Drop | Resend & Ack OK | Resend & Ack OK | PASS |
| D-1 | Database | Production SQLite PRAGMA Integrity | `integrity_check` | `ok` | `ok` | PASS |
| E-1 | Backup | Online SQLite Backup Creation | `t017_backup.py` | Backup DB Created | Backup DB Created | PASS |
| E-2 | Restore | Temporary Restore Integrity Verification | Restore to `/tmp` | Record Counts Match | Record Counts Match | PASS |
| F-1 | Security | Zero Committed Secrets in Git | Secret Scan | 0 Secrets Fired | 0 Secrets Fired | PASS |
| F-2 | Security | Non-root User Permissions | Ownership Check | `hidakamasato` | `hidakamasato` | PASS |
| F-3 | Security | LAN Only Access & CORS Whitelist | Header Check | Whitelisted | Whitelisted | PASS |
| G-1 | Monitoring | Monitoring Heartbeat & Alert Engine | `t016_monitor` | Alerts OPEN/RESOLVED | Alerts OPEN/RESOLVED | PASS |
| H-1 | LLM | Model Integrity & Q4_K_M GGUF Hash | GGUF Check | Qwen2.5-1.5B Valid | Qwen2.5-1.5B Valid | PASS |
| I-1 | Geocoder | Nominatim Rate Limit & Zero Hallucination | Safety Audit | Zero Centroids | Zero Centroids | PASS |
| J-1 | Engine | 50km Radius / 24h Window Merge Safety | Engine Test | Zero False Merges | Zero False Merges | PASS |
| K-1 | API/Web | Active Event Query Filter (`min_confidence=0.50`) | API Test | Resolved Only | Resolved Only | PASS |
| L-1 | Operations | Runbook (Cases 1-10) and RTO/RPO | Audit | RTO <30m, RPO <15m | RTO 2.2m, RPO 0m | PASS |
