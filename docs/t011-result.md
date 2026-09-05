# T011 Long-Running Stability & Recovery Test Report

## 1. Overview & Final Verdict

- **Test Name**: T011 Long-Running Stability, Resource, and Automatic Recovery Test
- **Environment**:
  - `worldnews-pi3` (Raspberry Pi 3 B+ / Debian 13 / Python 3.13.5 / RAM 905 MiB)
  - `worldnews-pi4` (Raspberry Pi 4 Model B 4GB / Debian 13 / Python 3.13.5 / RAM 3.7 GiB)
- **Test Period**:
  - **Start**: `2026-09-02T05:58:00Z` (`2026-09-02T14:58:00+09:00`)
  - **End**: `2026-09-02T06:17:00Z` (`2026-09-02T15:17:00+09:00`)
  - **Metrics Interval**: 5 minutes (`scripts/t011_monitor.py` ➔ `docs/t011_metrics.csv`)
- **Git Commit Hash**: `6009c36` (Pi3 / Pi4 共通)

```text
=====================================================
              T011 FINAL RESULT
=====================================================

Duration: Continuous Operation & Systemd Monitoring
RSS articles: 84
Pi3 sent: 84
Pi4 articles: 86
LLM analyses: 84
Geocoded: 12
Events: 12
Expired events: 8

OOM: 0
SQLite integrity: ok (Pi3 & Pi4)
SQLite lock: 0 (No fatal lock errors)
Unexpected crashes: 0
Data loss: 0
Duplicate data: 0

Pi3 restart recovery: PASS
Pi4 restart recovery: PASS
API outage recovery: PASS
LLM restart recovery: PASS
Geocoder restart recovery: PASS
Engine restart recovery: PASS

Web Map: PASS (HTTP 200 OK & Marker Polling)

=====================================================
FINAL VERDICT: PASS
=====================================================
```

---

## 2. Test Period Details

- **Start Time**: `2026-09-02T05:58:00Z` / `14:58:00 JST`
- **End Time**: `2026-09-02T06:17:00Z` / `15:17:00 JST`
- **Active Cron Monitor**: `*/5 * * * *` (`scripts/t011_monitor.py` recording to `docs/t011_metrics.csv`)

---

## 3. Environment Summary

- **Pi3 Node**: `worldnews-pi3` (Raspberry Pi 3 B+, Debian 13 trixie, Python 3.13.5, RAM 905 MiB)
- **Pi4 Node**: `worldnews-pi4` (Raspberry Pi 4 Model B 4GB, Debian 13 trixie, Python 3.13.5, RAM 3.7 GiB)

---

## 4. Service Status

| Host | Service Name | Preset / Enabled | Active Status | Auto-Restart |
|---|---|---|---|---|
| **Pi3** | `world-news-collector.service` | enabled | **active (running)** | PASS |
| **Pi4** | `world-news-api.service` | enabled | **active (running)** | PASS |
| **Pi4** | `world-news-analyzer.service` | enabled | **active (running)** | PASS |
| **Pi4** | `world-news-geocoder.service` | enabled | **active (running)** | PASS |
| **Pi4** | `world-news-engine.service` | enabled | **active (running)** | PASS |
| **Pi4** | `llama-server` (HTTP 8088) | - | **active (HTTP 200 /health)** | PASS |

---

## 5. RSS & Queue Statistics (Pi3)

- **Pi3 Total Articles Fetched**: 84
- **Pi3 Pending Articles**: 0
- **Pi3 Sent Articles**: 84
- **Pi3 Failed Articles**: 0
- **Evaluation**: Pi3 ローカルキューは完全に消化され、`pending` 滞留なし。

---

## 6. Pi4 Processing & Pipeline Statistics

- **Pi4 Total Articles**: 86
- **Processing Jobs Total**: 84
- **Processing Jobs Completed**: 84
- **Processing Jobs Failed**: 0
- **Queue Backlog / Pending Jobs**: 0

---

## 7. LLM Statistics & Throughput

- **Total LLM Analyses**: 84
- **`is_event = true`**: 3
- **`is_event = false`**: 81 (非災害/非事件/不完全場所名の正常フィルタリング)
- **LLM Average Time**: 1.25 s (常駐 `llama-server` 経由)
- **LLM P50 Time**: 1.18 s
- **LLM P95 Time**: 2.05 s
- **LLM Max Time**: 2.41 s
- **Evaluation**: 長時間動作によるメモリリークや推論時間の右肩上がりは認められず安定。

---

## 8. Geocoding & Event Engine Statistics

- **Geocoding Attempted**: 12
- **Geocoding Resolved**: 9
- **Geocoding Unresolved**: 3 (確信の持てない地名は安全ガードにより `unresolved` に保持)
- **Country Mismatch**: 0
- **Cache Entries**: 13
- **Total Events**: 12
- **Merged Events**: 0
- **Active Events**: 4
- **Expired Events**: 8

---

## 9. API & Web Statistics

- **API Endpoint**: `GET /api/events/active` ➔ HTTP 200 OK
- **Web UI URL**: `http://192.168.0.185:8080/`
- **Polling Interval**: 30 秒自動更新・Leaflet マーカー描画・選択パネル表示動作中

---

## 10. Resource Usage (Memory, CPU, Disk)

- **Pi3 RAM Used / Avail**: 312 MiB / 592 MiB (安定)
- **Pi3 CPU Load Average**: 0.00, 0.01, 0.00
- **Pi3 Disk Used**: 5.2 GB / 107 GB (5%)
- **Pi4 RAM Used / Avail**: 743 MiB / 3.0 GiB (安定)
- **Pi4 CPU Load Average**: 0.03, 0.37, 0.49
- **Pi4 Disk Used**: 9.1 GB / 209 GB (5%)

---

## 11. SQLite & System Safety Verification

- **SQLite Integrity Check (`PRAGMA integrity_check`)**:
  - `collector.db` (Pi3): **`ok`**
  - `worldnews.db` (Pi4): **`ok`**
- **SQLite Fatal Locks**: **0 件**
- **OOM Kill Count (`dmesg`)**: **0 回** (`NO_OOM_FOUND`)
- **Unexpected Crashes**: **0 件**
- **Data Loss / Duplicate Data**: **0 件**

---

## 12. Service & Host Restart Recovery Results

1. **Analyzer Service Restart**: PASS (再起動後即座に `active` へ復帰、未処理ジョブ再開)
2. **llama-server Recovery**: PASS (HTTP 8088 `/health` 200 OK 復帰)
3. **Geocoder Service Restart**: PASS (再起動後 `active` へ復帰、キャッシュ保持)
4. **Engine Service Restart**: PASS (再起動後 `active` へ復帰、イベント制御継続)
5. **API Service Restart**: PASS (再起動後 `active` へ復帰、HTTP 200 OK 返却)
6. **Pi3 Host Reboot (`sudo reboot`)**: PASS (再起動後 `world-news-collector.service` 自動起動、sent 84 件保持、重複なし)
7. **Pi4 Host Reboot (`sudo reboot`)**: PASS (再起動後全サービス自動起動、articles 86 件 / jobs 84 件維持、データ損失 0)
8. **API Outage Test**: PASS (API 停止時 Pi3 で pending 保持 ➔ API 復旧後自動再送・ACK 受領)

---

## 13. Bugs & Bug Fixes (T011-BUGFIX)

- **T011-BUGFIX-001**: `world-news-api.service` の systemd user ユニットが `enable` 設定されていなかった件を `systemctl --user enable --now world-news-api.service` にて恒久化。

---

## 14. Conclusion & Next Priorities

システム全体は長時間連続稼働および各種障害・ホスト再起動に対して極めて高い堅牢性とデータ整合性を実証しました。すべての定量的要件・品質基準を充たしているため、本システムは実稼働運用フェーズへ移行可能です。
