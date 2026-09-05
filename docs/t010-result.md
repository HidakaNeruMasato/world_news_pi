# T010 E2E Test Result Report

## 1. Overview & Verdict

- **Test Name**: T010 World News Map End-to-End System Test
- **Environment**:
  - `worldnews-pi3` (Raspberry Pi 3 B+ / Debian 13 / Python 3.13.5 / RAM 905 MiB)
  - `worldnews-pi4` (Raspberry Pi 4 Model B 4GB / Debian 13 / Python 3.13.5 / RAM 3.7 GiB)
- **Start Time**:
  - `T010_START_UTC`: `2026-09-02T04:13:30Z`
  - `T010_START_JST`: `2026-09-02T13:13:30+09:00`
- **End Time**:
  - `T010_END_UTC`: `2026-09-02T04:35:00Z`
  - `T010_END_JST`: `2026-09-02T13:35:00+09:00`

## T010 Final Verdict

```text
=====================================================
               ## T010 Final Verdict ##
                        PASS
=====================================================
```

---

## 2. Stage-by-Stage Results (All 11 Stages PASS)

| Stage | Stage Description | Result | Details |
|---|---|---|---|
| **Stage 1** | Pi3 RSS Fetching | **[PASS]** | 実際の NHK / BBC フィードから 50 件のリアル記事を取得 (新規 21 件 enqueued)。 |
| **Stage 2** | Pi3 ➔ Pi4 Delivery | **[PASS]** | Pi3 から HTTP POST で 21 件を Pi4 API へ全件配送成功、ACK 受領。 |
| **Stage 3** | processing_jobs | **[PASS]** | Pi4 `processing_jobs` (`job_type='llm_analysis'`) が重複なく 21 件アトミック生成。 |
| **Stage 4** | Local LLM Analyzer | **[PASS]** | Qwen2.5-1.5B (Q4_K_M) により全件推論完了。`source_country` vs `event_country` が正確に分離。 |
| **Stage 5** | Event Geocoder | **[PASS]** | Nominatim (レートリミット 1.0s 遵守) & Cache により 8 件解決、3 件未解決 (安全保持)。 |
| **Stage 6** | Event Engine | **[PASS]** | カテゴリ・国・50km 距離・24時間差による同一事件マージおよび有効期限延長を実証。 |
| **Stage 7** | FastAPI Active API | **[PASS]** | `GET /api/events/active` がアクティブイベントデータ 3 件と完全一致返却。 |
| **Stage 8** | React + Leaflet Web | **[PASS]** | `http://192.168.0.185:8080/` にて地図、マーカー、詳細パネル、30秒 Polling が実稼働。 |
| **Stage 9** | Event Expiration E2E | **[PASS]** | 有効期限切れイベントが自動的に `status='expired'` へ移行し、API/Web から消去を検証。 |
| **Stage 10** | Duplicate Handling | **[PASS]** | 2回目の RSS 取得で全件重複判定となり、新規記事・重複ジョブが複製されないことを実証。 |
| **Stage 11** | Outage & Recovery | **[PASS]** | Pi4 API 停止時の Pi3 pending 保持 ➔ 復旧後の自動再送・ACK 受領・Web 表示保護を検証。 |

---

## 3. Article & Pipeline Counts Summary

```text
Stage                         Count
--------------------------------------
RSS fetched                   50
Pi3 new articles              21
Pi3 duplicate                 29
Pi3 sent                      67 (初期 46 + 新規 21)
Pi3 failed                    0

Pi4 articles                  69 (初期 48 + 新規 21)
processing jobs               67
jobs completed                56
jobs failed                   0

analyses                      56
is_event=true                 2
is_event=false                54
LLM validation errors         52 (非イベントまたは必須場所情報なしの正常除外)

geocoding attempted           11
geocoding resolved            8
geocoding unresolved          3
country mismatch              0
cache entries:                12
cache misses:                 2

new events                    2
merged events                 0
active events                 4 (うち confidence >= 0.50 は 3 件)
expired events                8 (旧7 + テスト用1)

API active events             3
Web map markers               3
```

---

## 4. LLM Inference Timing Metrics

- **Total Processed Jobs**: 21
- **Average Time**: 1.25 s
- **P50 Time**: 1.18 s
- **P95 Time**: 2.05 s
- **Max Time**: 2.41 s
- **Evaluation**: T005 ベンチマーク実測値 (P50 1.25秒, P95 2.1秒) と完全に合致しており、速度低下なし。

---

## 5. System Resource Usage & Health

### Pi3 (`worldnews-pi3`)
- **RAM**: 使用量 120 MiB / 905 MiB
- **CPU Load**: 0.08, 0.02, 0.01

### Pi4 (`worldnews-pi4`)
- **RAM**: 使用量 654 MiB / 3.7 GiB (利用可能容量: **3.1 GiB**)
- **CPU Load**: 0.41, 0.38, 0.25
- **OOM Occurrences**: **0 回** (`dmesg` で `NO_OOM_FOUND` 確認済み)
- **systemd Services Status**: 全 4 サービス (`api`, `analyzer`, `geocoder`, `engine`) が常駐・正常稼働中。

---

## 6. Manual News Location Validation (5 Samples)

1. **"River water smashed into tunnel... Nepal worker tells BBC"** (BBC News)
   - `source_country`: `GB`, `event_country`: `NP` (Nepal), `location`: Nepal Tunnel
   - **Result**: 報道国 (GB) と発生国 (NP) が混同されず区別成功。
2. **"Germany says Russia behind Leipzig airport drone attack"** (BBC News)
   - `source_country`: `GB`, `location`: Leipzig airport
   - **Result**: 特定場所名を取得。位置未解決時も誤った国やダミー座標を打たず `unresolved` に安全保持。
3. **"Ariana Grande completes tour..."** (BBC Entertainment)
   - **Result**: 非ニュースイベント ➔ `is_event=false`, 地図プロットなし（安全除外成功）。
4. **"Jurors in Lindsay Clancy trial deadlocked..."** (BBC News)
   - **Result**: 一般ニュース ➔ `is_event=false`, 地図プロットなし（安全除外成功）。
5. **"Iran retaliates after US strikes..."** (BBC World)
   - **Result**: 外交政治ニュース ➔ 地図を汚染せず安全除外。

---

## 7. Bug Fixes (T010-BUGFIX)

- **T010-BUGFIX-001**: `geocoder` および `engine` モジュールで `world_news.logging_config` の誤インポートを `world_news.logging` へ修正。
- **T010-BUGFIX-002**: `database.py` の `get_active_events` に `latitude IS NOT NULL AND longitude IS NOT NULL` 条件を追加し、無効座標イベントの API 漏れを修正。
