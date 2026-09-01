# ARCHITECTURE.md — システムアーキテクチャ

## 1. ノード分割と役割

```text
┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐
│  worldnews-pi3 (Raspberry Pi 3 B+)   │     │  worldnews-pi4 (Raspberry Pi 4 4GB)  │
│  - RSS / Atom 取得                   │     │  - REST API (FastAPI / Uvicorn)      │
│  - 正規化 & 重複排除                 │ ──► │  - SQLite カノニカル DB (worldnews.db)│
│  - ローカル永続キュー (collector.db)  │ HTTP│  - 原子的 Transaction (Articles/Jobs) │
│  - At-Least-Once / ACK 配送管理      │ POST│  - LLM 解析ジョブ管理 (T006予定)     │
└──────────────────────────────────────┘     └──────────────────────────────────────┘
```

## 2. データ配送フローとトランザクション保証 (Pi3 ➔ Pi4)

1. **Pi3 Collector**: RSS/Atom から記事を取得・正規化し、SQLite (`collector.db`) に `status='pending'` で保存。
2. **HTTP 送信**: Pi3 は Pi4 REST API (`POST /api/v1/internal/articles`) へ記事ペイロードを送信。
3. **Pi4 原子的トランザクション**:
   - `external_id`, `url`, `content_hash` による重複チェック。
   - 重複時: DB 書き込みスキップ ➔ `200 OK` (ACK: `already_exists`)。
   - 新規時: SQLite トランザクション (`BEGIN IMMEDIATE`) 内で `articles` への INSERT と `processing_jobs` (`job_type='llm_analysis'`, `status='pending'`) への INSERT を同時実行 ➔ `COMMIT` ➔ `201 Created` (ACK: `created`)。
4. **Pi3 ACK 処理**:
   - HTTP 200/201 (ACK) を受領した記事のみ SQLite ステータスを `sent` に変更。
   - Pi4 停止またはエラー時は `pending` のまま安全に保持し、指数バックオフで再送試行。

## 3. 国情報の分離原則

- **`source_country`**: RSS ニュース発行元の国コード (例: JP, GB, US)。Pi3 および Pi4 `articles.source_country` で一貫保持。
- **`event_country`**: ニュース記事が対象とする「事件・発生国」。LLM 解析フェーズ (T006) で抽出される別フィールドであり、絶対に `source_country` と同一扱いしません。
