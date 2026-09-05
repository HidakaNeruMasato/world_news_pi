# T018 — Production Operation / 7-Day Observability Validation

This directory contains the 7-day continuous production operation audit records, daily snapshots, resource memory leak analyses, human event quality reviews, anomaly logs, and final operational acceptance reports for T018.

## Files & Directories
- `README.md`: Directory sitemap
- `operation-plan.md`: 7-day continuous operation and observability plan
- `environment.md`: Production hardware nodes and infrastructure baseline
- `metrics-schema.md`: Metrics collection schema and parameters
- `anomalies.md`: Recorded metric anomalies during 7-day operation
- `incidents.md`: Recorded incident logs during 7-day operation
- `quality-review.md`: 50 real-world event human review audit
- `resource-analysis.md`: 7-day memory leak, CPU, and disk trend analysis
- `pipeline-analysis.md`: End-to-end processing pipeline analysis
- `monitoring-analysis.md`: T016 monitoring heartbeat and alert analysis
- `results.md`: T018 final operation summary and Verdict (PASS / CONDITIONAL PASS / FAIL)
- `regression.md`: Full safety regression and unit test verification report
- `daily/`: Daily Markdown reports (`day-01.md` to `day-07.md`)
- `snapshots/`: Daily UTC JSON snapshots (`day-01.json` to `day-07.json`)
