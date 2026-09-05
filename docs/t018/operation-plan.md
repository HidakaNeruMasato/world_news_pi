# T018 7-Day Continuous Operation & Observability Plan

## 1. Objectives & Scope
- **Duration**: Minimum 7 days continuous operation (Day 01 to Day 07).
- **Core Principle**: Zero changes to Qwen2.5-1.5B, Prompt v2, Threshold 0.35, Geocoder, Event Engine, API, and Web Map UI.
- **Goal**: Collect multi-node metrics, analyze pipeline performance, run 50 real-event human reviews, verify 7-day memory stability, and issue final Verdict (`PASS` / `CONDITIONAL PASS` / `FAIL`).

---

## 2. Success Criteria & Thresholds

| Category | Success Criterion | Target Standard |
|---|---|:---:|
| Operational Duration | Continuous 7-Day Execution | >= 7 Days |
| Data Integrity | Data Loss / Database Corruption | **Strictly 0** |
| Map Safety | Critical Map Errors (Fake events/coords, Country Centroids) | **Strictly 0** |
| Delivery Success | Pi3 -> Pi4 Ingestion Delivery Success | >= 99.0% |
| LLM Success Rate | LLM Processing Job Success Rate | >= 95.0% |
| API Availability | `/api/health` and `/api/events/active` HTTP 200 | >= 99.0% |
| Web Availability | Map UI (`:8080`) HTTP 200 | >= 99.0% |
| Queue Backlog | Permanent Backlog Accumulation | **0** |
| Memory Stability | Continuous Monotonic Memory Leak | **No Leak Detected** |
| Disk Storage | Max Disk Space Usage | < 80.0% |
