# T025 外部ユーザーテスト環境設計書 (docs/t025/t025-environment-design.md)

## 1. 目的

World News Map の一般ユーザー向け初見 UX 検証（2〜3名の友人テスター）において、**本番環境（Production Pi3 / Pi4 / SQLite / LLM / SSH / 内部API）を完全に保護・非公開**にし、安全かつ快適に体験してもらうための環境構成を定義します。

---

## 2. システムアーキテクチャ

```text
                             Internet
                                │
                                ▼
                       ┌─────────────────┐
                       │ GitHub Pages    │
                       │ Friend Web UI   │
                       └────────┬────────┘
                                │ HTTPS
                                ▼
                       ┌─────────────────┐
                       │ Friend Test API │
                       │ Read Only       │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Friend Test DB  │
                       │(worldnews_test) │
                       └─────────────────┘


Production (完全保護・非公開)

                       ┌─────────────────┐
                       │ Raspberry Pi 3  │
                       │ RSS Collector   │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Raspberry Pi 4  │
                       │ Production      │
                       │ API / LLM / etc │
                       └────────┬────────┘
                                │
                                ▼
                       Production DB
                       (worldnews.db)
```

---

## 3. コンポーネントおよび境界設計

### 1. Friend Web UI (GitHub Pages)
- **配信元**: GitHub Pages (`https://<user>.github.io/...`)
- **API Base URL**: `VITE_API_BASE_URL` 環境変数を使用（`192.168.0.x` のような本番 LAN IP やフォールバック接続は 100% 排除）。

### 2. Friend Test API (`friend_api.py`)
- **読み取り専用制御**: 全 `POST`, `PUT`, `PATCH`, `DELETE` リクエストを `405 Method Not Allowed` / `403 Forbidden` で遮断。
- **データソース拘束**: `worldnews_test.db` のみに接続（本番 `worldnews.db` へのクエリ経路を物理的に持たない）。
- **内部機能遮断**: `/api/v1/internal/*`, `/api/dashboard/*`, `/api/v1/stats` を `403 Forbidden` で遮断。
- **CORS 制限**: GitHub Pages Origin および指定されたテスト環境 Origin のみ許可。ワイルドカード `*` 非許可。
- **Rate Limiting**: クライアント IP 単位で 60 req/min に制限（超過時 `429 Too Many Requests`）。
- **キャッシュ最適化**: `GET /api/events/active` に 15秒 TTL のインメモリキャッシュを設定しスパイク負荷を吸収。

### 3. Friend Test DB (`worldnews_test.db`)
- 本番 DB からのリードオンリースナップショットスクリプト (`scripts/t025_create_test_db.py`) により作成。
- 120 イベント、824 記事および T024 多様状態 (`ACTIVE`, `REDIRECTED`, `NOT_FOUND`, `GONE`, `BLOCKED`, `TEMPORARY_UNAVAILABLE`) を格納。
