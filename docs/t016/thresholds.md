# T016 Monitoring Threshold Rules

| Component | Metric | WARNING Threshold | ERROR Threshold | CRITICAL Threshold |
|---|---|---|---|---|
| RSS Feed | Consecutive Failures | >= 3 failures | >= 10 failures | — |
| RSS Feed | Stale Ingestion | > 6 hours | > 12 hours | — |
| Delivery Queue | Pending Backlog | >= 20 jobs | >= 50 jobs | >= 100 jobs |
| LLM Analyzer | Error Rate | > 2.0% | > 5.0% | > 10.0% |
| LLM Analyzer | P95 Latency | > 5.0 sec | > 10.0 sec | > 30.0 sec |
| Disk Free Space | Storage Free % | < 30% free | < 20% free | < 10% free |
| System Services | Service Status | Restart count > 0 | > 3 restarts/10m | Service FAILED |
| Database | PRAGMA Integrity | — | — | Integrity Check Fail |
| Coordinate Safety | Lat/Lng Schema | — | — | Lat/Lng on Unresolved |
| Monitor Heartbeat| Stale Run | > 15 min stale | > 30 min stale | — |
