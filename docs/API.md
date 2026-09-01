# API.md — Pi4 REST API 仕様書

## 1. 概要 (Overview)

- **バージョンプレフィックス**: `/api/v1`
- **フレームワーク**: FastAPI (Uvicorn)
- **バインドポート**: 8080 (LAN内限定アクセス)

---

## 2. GET /api/v1/health

サービスヘルスチェック・コンポーネント状態。

### レスポンス例 (200 OK)
```json
{
  "status": "ok",
  "database": "ok",
  "queue": "ok",
  "llm": "not_configured"
}
```
※ T004 時点では LLM は未実装のため、`"llm": "not_configured"` を返します。

---

## 3. POST /api/v1/internal/articles

Pi3 からの正規化ニュース記事の受領内部 API (At-Least-Once / 冪等性対応)。

### リクエストボディ (JSON)
```json
{
  "source_id": 1,
  "source_country": "JP",
  "external_id": "guid-123",
  "title": "台風24号 2日～4日ごろに沖縄・奄美に近づく見込み",
  "description": "サマリーテキスト...",
  "url": "https://www.nhk.or.jp/news/html/...",
  "published_at": "2026-09-01T12:00:00+00:00",
  "fetched_at": "2026-09-01T12:05:00+00:00",
  "language": "ja",
  "content_hash": "sha256_hash_string"
}
```

### レスポンス仕様および ACK 挙動

1. **新規登録成功 (201 Created)**:
   - 単一の SQLite トランザクションで `articles` および `processing_jobs` (`job_type='llm_analysis'`) が安全に作成された場合。
   ```json
   {
     "status": "created",
     "article_id": 123,
     "message": "Article ingested and processing job created"
   }
   ```
2. **重複受領 (200 OK - ACK)**:
   - `external_id`, `url`, `content_hash` に基づき既存記事を検知した場合。重複レコードや重複ジョブは作成せず、Pi3 側が送信完了 (`sent`) と判断できる ACK を返します。
   ```json
   {
     "status": "already_exists",
     "article_id": 123,
     "message": "Article already exists, ACK acknowledged"
   }
   ```
3. **バリデーションエラー (400 Bad Request / 422 Unprocessable Entity)**:
   - `title` が空文字、必須項目欠落、不正データ形式の場合。

---

## 4. GET /api/v1/events

アクティブイベント一覧 (T004 時点は0件プレースホルダー)。

### レスポンス例 (200 OK)
```json
{
  "events": [],
  "count": 0
}
```

---

## 5. GET /api/v1/stats

システム統計情報。

### レスポンス例 (200 OK)
```json
{
  "active_events": 0,
  "pending_articles": 10,
  "processed_articles": 0,
  "failed_articles": 0,
  "total_articles": 10,
  "pending_jobs": 10,
  "failed_jobs": 0
}
```
