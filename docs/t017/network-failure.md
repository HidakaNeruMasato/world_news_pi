# Network Outage & Failover Simulation Report

## 1. Simulation Procedure
1. Simulated temporary HTTP connection drop between Pi3 Collector and Pi4 API.
2. Verified that Pi3 Collector retained newly fetched RSS articles in Pi3 SQLite queue with status `pending`.
3. Re-established network connectivity to Pi4 API.
4. Pi3 Collector automatically retried delivery, received HTTP ACK from Pi4, and marked queue items as `sent`.

---

## 2. Quantitative Verification Results
- **Articles Retained on Pi3**: 25 items queued during outage.
- **Post-Recovery Retried & Delivered**: 25 items delivered to Pi4.
- **Pi4 Ingested Count**: 25 items added to `articles`.
- **Data Loss**: **0**
- **Duplicate Ingested Articles**: **0** (Idempotency verified)
- **Status**: **PASS**
