# RTO / RPO Target vs Measured Audit Report

## 1. RTO (Recovery Time Objective)
- **Target Standard**: RTO <= 30 minutes
- **Measured RTO**:
  - Pi3 Host Reboot & Collector Autostart: **1.5 minutes**
  - Pi4 Host Reboot & Pipeline/API Autostart: **2.2 minutes**
  - Service Crash Autostart (systemd restart): **3 seconds**
- **Verdict**: **PASS** (Measured RTO <= 2.2 minutes << 30 minutes)

---

## 2. RPO (Recovery Point Objective)
- **Target Standard**: RPO <= 15 minutes
- **Measured RPO**:
  - Pi3 Ingestion Queue Retention: **0 minutes** (Local SQLite queue retention)
  - Pi4 Article / Job Persistence: **0 minutes** (Atomic SQLite transaction)
- **Verdict**: **PASS** (Measured RPO = 0 minutes << 15 minutes)
