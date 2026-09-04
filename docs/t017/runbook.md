# Production Incident Response Runbook (Cases 1 to 10)

## Case 1: Pi3 Node Down
- **Symptom**: `world-news-collector.service` unreachable or Pi3 offline.
- **Verification**: `ssh hidakamasato@192.168.0.149 "uptime"`
- **Recovery**: Restart Pi3 host. Verified Pi3 SQLite queue retains unacknowledged items.

## Case 2: Pi4 Node Down
- **Symptom**: Web UI and API HTTP 500 / Connection Refused.
- **Verification**: `ssh hidakamasato@192.168.0.185 "systemctl --user status world-news-api"`
- **Recovery**: Restart Pi4 host. All systemd services autostart on boot.

## Case 3: Collector Stopped
- **Recovery**: `systemctl --user restart world-news-collector.service`

## Case 4: API Outage
- **Recovery**: `systemctl --user restart world-news-api.service`

## Case 5: LLM Process Down
- **Recovery**: Restart LLM server. Worker retries queued jobs automatically.

## Case 6: Geocoder Outage
- **Recovery**: `systemctl --user restart world-news-geocoder.service`

## Case 7: SQLite Integrity Check Error
- **Recovery**: Execute online restore from `t017_backup.py` backup file.

## Case 8: Disk Full Warning
- **Recovery**: Run log cleanup: `journalctl --vacuum-size=100M`

## Case 9: Network Interruption
- **Recovery**: Verify Pi3 queue retention; automatic resend occurs when link restores.

## Case 10: Heavy Queue Backlog
- **Recovery**: Inspect LLM worker logs; check P95 latency; restart analyzer if stuck.
