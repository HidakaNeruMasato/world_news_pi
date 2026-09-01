# RSS.md — Pi3 Collector 仕様およびローカルキュー状態遷移

## 1. Feed Registry (フィード管理)

各フィードは設定データ (YAML / Config) として管理されます:

- `id`: フィード一意ID
- `name`: ソース名
- `source_country`: 発行元国コード (例: JP, GB, US) ※イベント発生国とは区別
- `language`: 言語コード (例: ja, en)
- `feed_url`: RSS/Atom URL
- `category`: カテゴリ
- `enabled`: 有効フラグ (boolean)
- `interval_seconds`: 取得インターバル (秒)
- `timeout_seconds`: タイムアウト時間 (秒)

## 2. RSS / Atom パースおよび正規化

- **対応フォーマット**: RSS 2.0 および Atom 1.0 (XML 要素フォールバック処理付き)
- **正規化フィールド**: `source_id`, `source_country`, `external_id`, `title`, `description`, `url`, `published_at`, `fetched_at`, `language`, `content_hash`
- **制限**: 本文スクレイピングは一切行わず、RSS/Atom で配信されるサマリー/説明文のみを使用します。

## 3. 重複排除 (Deduplication) 優先度

1. `external_id` (GUID / Atom ID)
2. canonical `url`
3. `content_hash` (SHA256: `title|description|url`)
4. `title` + `source_id`

## 4. Pi3 ローカルキュー状態遷移 (Queue State Semantics)

Pi3 はローカル SQLite (`collector.db`) を使用して配送キューを管理します。

```text
       [RSS/Atom Feed]
              │
              ▼ (enqueue_article)
        ┌───────────┐
        │  PENDING  │ ◄──────┐ (リトライ待機: 指数バックオフ)
        └─────┬─────┘        │
              │              │
              ▼              │
        ┌───────────┐        │ (ACK 未受領 / 通信失敗)
        │  SENDING  │ ───────┤
        └─────┬─────┘        │
              │ (ACK 受領)   │ (最大リトライ超過)
              ▼              ▼
        ┌───────────┐  ┌───────────┐
        │   SENT    │  │  FAILED   │
        └───────────┘  └───────────┘
```

- **`pending`**: 取得・正規化済み、Pi4 への配送待ち（DB 永続化済み）。
- **`sending`**: Pi4 への POST 送信処理中。
- **`sent`**: Pi4 から HTTP 200 OK / 201 Created (ACK) を正常受領した完了状態。
- **`failed`**: 最大リトライ回数 (デフォルト 5回) を超過したリトライ不可状態。

## 5. 耐障害性とAt-Least-Once配送

- **障害隔離**: 1つのフィードがタイムアウトや XML エラーで失敗した場合でも、他のフィード処理は継続されます。
- **Pi4 停止耐性**: Pi4 が停止中の場合、記事は `pending` 状態のまま SQLite に安全に保持され、Pi4 復旧後に自動再送されます。
- **再起動耐性**: Pi3 プロセスや OS が再起動しても、SQLite に保存された `pending` 記事は失われません。
