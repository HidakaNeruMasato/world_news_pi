# End-to-End Processing Pipeline Observability Analysis

## 1. Intake & Delivery Flow
- **Articles Collected on Pi3**: 3,640 items (24h avg: 520 items)
- **Delivery Success Rate**: **100.0%** (3,640 delivered / 3,640 collected)
- **Queue Pending Backlog**: **0** (All items processed and ACKed)

---

## 2. LLM Analyzer Performance Trend
- **Total Ingested Jobs**: 3,640 jobs
- **Completed Jobs**: 3,640 jobs
- **Failed / Dropped Jobs**: 0 jobs (**100.0% LLM Success Rate**)
- **P50 Latency**: 1.25 seconds
- **P95 Latency**: 2.10 seconds

---

## 3. Geocoder & Event Engine
- **Geocoding Attempted**: 3,640 items
- **Resolved Items**: 2,366 items (65.0% resolution rate)
- **Unresolved Items**: 1,274 items (35.0% unresolved due to generic/no location)
- **Country Mismatches Rejected**: 0
- **Events Created**: 945 events
- **Events Merged**: 126 events (1.13 articles/event average)
