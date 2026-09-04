# T017 — Production Readiness / Operational Acceptance

This directory contains complete production readiness audits, backup/restore verification, failover testing, runbooks, RTO/RPO definitions, security audits, and final operational acceptance results for T017.

## Files
- `README.md`: Directory sitemap
- `architecture.md`: Configuration Freeze specification and component data durability matrix
- `deployment-audit.md`: Phase 0 Pi3/Pi4 node system inventory (Expected vs Actual comparison)
- `reboot-recovery.md`: Host reboot recovery verification and zero data loss proof
- `backup-restore.md`: SQLite online backup (`.backup`) and temporary restore verification
- `security-audit.md`: Secret scan, CORS, and permission audit report
- `resource-audit.md`: Disk, RAM, log rotation, and resource audit report
- `network-failure.md`: Network outage simulation, Pi3 queueing, automatic ACK and retry report
- `rss-failure.md`: RSS feed failure, isolation, and alert detection report
- `llm-failure.md`: LLM Analyzer failure, retry/backoff, and zero data loss report
- `geocoder-failure.md`: Geocoder failure, unresolved location safety, and zero centroid report
- `monitoring-self-test.md`: Monitoring heartbeat self-test and alert recovery report
- `runbook.md`: Incident response procedures for Cases 1 to 10
- `incident-response.md`: Emergency primary response flow
- `rto-rpo.md`: Target vs measured RTO (<30m) and RPO (<15m) report
- `acceptance-criteria.md`: Complete Production Readiness Checklist (A to L)
- `results.md`: T017 final acceptance summary and Final Verdict (PRODUCTION READY / CONDITIONAL READY)
- `regression.md`: Safety regression and unit test verification report
