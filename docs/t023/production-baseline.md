# T023 Production Baseline

## 1. Environment Baseline

* **Production URL**: `http://192.168.0.185:8080/` (Local binding: `http://localhost:8080/`)
* **Git Baseline Commit**: `080f597992ef6289dafb3ab1f5c7245013527e39`
* **Git Commit Message**: `T022-2: implement UI UX and information architecture refinement`
* **Git Status**: Working tree clean (untracked scratch inspection tools preserved)
* **Pytest Suite Result**: `337 PASSED` (323 existing + 14 T023 automated UX tests)
* **TypeScript / Vite Build**: `PASS` (`dist/index.html`, `dist/assets/index-*.js` 343.4 kB)
* **SQLite Integrity Check**: `ok`
* **Production DB Writes**: `0`

---

## 2. Production Event Population Snapshot

* **Active Events Count**: `120`
* **Total Events in Database**: `120`
* **Events with Unknown/Unresolved Location**: `0`
* **Multi-Article Events (`article_count > 1`)**: `0` (Production DB) / `10+` (Simulated Sandbox Multi-Article Validation)
* **Single-Article Events (`article_count == 1`)**: `120`

### Regional Breakdown

| Region | Event Count | Percentage |
|---|---:|---:|
| **Europe** | 27 | 22.5% |
| **Africa** | 26 | 21.7% |
| **Asia** | 24 | 20.0% |
| **Americas** | 18 | 15.0% |
| **Middle East** | 17 | 14.2% |
| **Oceania** | 8 | 6.7% |
| **Total** | **120** | **100.0%** |

### Category Breakdown

| Category | Event Count | Percentage |
|---|---:|---:|
| **politics** | 36 | 30.0% |
| **economy** | 31 | 25.8% |
| **earthquake** | 18 | 15.0% |
| **infrastructure_failure** | 10 | 8.3% |
| **wildfire** | 10 | 8.3% |
| **storm** | 8 | 6.7% |
| **flood** | 4 | 3.3% |
| **volcanic_eruption** | 3 | 2.5% |

### Top 15 Country Distribution

| Country Code | Event Count |
|---|---:|
| **KE** (Kenya) | 10 |
| **DE** (Germany) | 9 |
| **JP** (Japan) | 8 |
| **AE** (United Arab Emirates) | 7 |
| **PK** (Pakistan) | 7 |
| **GB** (United Kingdom) | 7 |
| **BR** (Brazil) | 7 |
| **EG** (Egypt) | 6 |
| **NG** (Nigeria) | 6 |
| **QA** (Qatar) | 5 |
| **IL** (Israel) | 5 |
| **NZ** (New Zealand) | 5 |
| **MX** (Mexico) | 5 |
| **RO** (Romania) | 4 |
| **RS** (Serbia) | 4 |
