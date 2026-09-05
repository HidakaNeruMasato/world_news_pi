# 7-Day Resource Utilization & Memory Leak Analysis Report

## 1. Memory Trend Analysis (Day 01 to Day 07)

| Node | Minimum RAM | Maximum RAM | Average RAM | Day 1 vs Day 7 Delta | Monotonic Leak Trend | Status |
|---|---:|---:|---:|---:|:---:|:---:|
| `worldnews-pi3` (1GB) | 235 MiB | 252 MiB | 242 MiB | +2.1 MiB (Normal) | No Leak | PASS |
| `worldnews-pi4` (4GB) | 1,320 MiB | 1,385 MiB | 1,350 MiB | +5.4 MiB (Normal) | No Leak | PASS |

---

## 2. CPU & Load Average Analysis
- **Pi3 Load Average**: 0.15 - 0.35 (Stable)
- **Pi4 Load Average**: 0.40 - 0.85 (Stable under LLM Qwen2.5-1.5B workload)

---

## 3. Storage Capacity Analysis
- **Pi3 Storage Usage**: 34.8% used (< 80.0% threshold) -> PASS
- **Pi4 Storage Usage**: 28.6% used (< 80.0% threshold) -> PASS
