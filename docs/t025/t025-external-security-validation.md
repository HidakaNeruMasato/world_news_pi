# T025-1 外部公開最終セキュリティ検証結果報告書 (External Security Validation)

## 1. 実施概要

* **実施日時**: 2026-09-10T14:50:00+09:00
* **検証環境**: World News Map 外部ユーザーテスト環境 (Friend Test Environment v0.2.5)
* **検証目的**: 2〜3名の友人外部テスターへ URL を安全に公開するため、本番インフラ (Production Pi3/Pi4/`worldnews.db`/LLM) が完全に保護・隔離されていること、および Friend API / Web UI がセキュリティ基準を満たしていることを実環境で最終検証する。
* **判定結果**: **PASS (友人テスト公開承認)**

---

## 2. 外部公開ネットワーク構成 (Topology)

```text
【外部テスター公開エリア (Internet)】
  ユーザー (PC / スマホ 4G/5G)
      │
      ├──> GitHub Pages (HTTPS: https://<user>.github.io/world-news-map/)
      │       │
      │       └──> Friend Test API (HTTPS / Read-Only FastApi Server)
      │               │
      │               └──> worldnews_test.db (リードオンリースナップショット DB)

【本番保護エリア (Internet 完全非公開・LAN 隔離)】
  Production Pi3 ──> Production Pi4 ──> Production worldnews.db
    - API (Port 8080): Internet 未公開 (Connection Refused / Blocked)
    - SSH (Port 22)  : Internet 未公開 (Connection Refused / Blocked)
    - LLM (Port 8081): Internet 未公開 (Connection Refused / Blocked)
```

---

## 3. Security Gate & UX Gate チェック結果

### 3-1. Security Gate Checklist

| # | チェック項目 | 判定 | 備考 |
|---|---|---|---|
| 1 | Production DB Internet 非公開 | **PASS** | LAN 外アクセス不可 |
| 2 | Production API (Port 8080) Internet 非公開 | **PASS** | 外部 IP ルーティングなし |
| 3 | Pi3/Pi4 SSH (Port 22) Internet 非公開 | **PASS** | 外部アクセス拒否 |
| 4 | llama-server (Port 8081) Internet 非公開 | **PASS** | 外部アクセス拒否 |
| 5 | Friend API のみ外部公開 | **PASS** | Read-Only エンドポイントのみ |
| 6 | Friend API は `worldnews_test.db` のみ使用 | **PASS** | `worldnews.db` 接続ルートなし |
| 7 | Write API (POST/PUT/DELETE) 拒否 | **PASS** | 405 Method Not Allowed / 403 |
| 8 | Internal API (`/api/v1/internal/*`) 拒否 | **PASS** | 403 Forbidden で完全ブロック |
| 9 | Admin エンドポイント (`/admin`) 拒否 | **PASS** | 403 Forbidden |
| 10 | 任意 URL SSRF (Link Checker API) 非搭載 | **PASS** | エンドポイント非公開 |
| 11 | CORS 制限 | **PASS** | `*` 拒否、許可された Origin のみ |
| 12 | HTTPS 通信 | **PASS** | 暗号化チャネル経由のみ |
| 13 | Rate Limiting (60 req/min/IP) | **PASS** | 超過時 429 Too Many Requests |
| 14 | Production Credentials 非混入 | **PASS** | Secret 走査結果 0 件 |
| 15 | Production IP (`192.168.0.x`) 非混入 | **PASS** | ビルド内 IP 検出 0 件 |
| 16 | Production DB 非侵襲 | **PASS** | `PRAGMA integrity_check` = ok |

### 3-2. UX Gate Checklist

| # | チェック項目 | 判定 | 備考 |
|---|---|---|---|
| 1 | Map / Leaflet 表示 | **PASS** | 全要素正常レンダリング |
| 2 | Cluster 表示 | **PASS** | マーカークラスタリング動作 |
| 3 | Region Filter 動作 | **PASS** | 7地域フィルター連動 |
| 4 | Country Filter 動作 | **PASS** | 国コード絞り込み |
| 5 | Category Filter 動作 | **PASS** | イベント種別フィルター |
| 6 | Event List | **PASS** | リスト選択・地図同期 |
| 7 | Event Detail Panel | **PASS** | イベント詳細表示 |
| 8 | Multi-Article サポート | **PASS** | 複数記事の比較表示 |
| 9 | Article Preview | **PASS** | 概要カード保護表示 |
| 10 | Original Article Link | **PASS** | 元記事への遷移 |
| 11 | Alternative Article | **PASS** | 代替記事の提示 |
| 12 | T024 URL 障害状態表示 | **PASS** | 6 状態別の警告・代替 UI |
| 13 | Mobile UI 応答性 | **PASS** | タッチ操作・レスポンシブ表示 |

---

## 4. 境界テストケース (Case A 〜 G) 実地検証結果

| ケース | 内容 | 期待結果 | 実行結果 | 判定 |
|---|---|---|---|---|
| **Case A** | Friend Web UI 通常 GET 操作 | HTTP 200 / 正常データ返却 | Health: 200, Active Events: 200 | **PASS** |
| **Case B** | Friend API 書き込み URL 直叩き | HTTP 405 / 403 拒否 | POST: 405, DELETE: 405 | **PASS** |
| **Case C** | Production Internal API 直叩き | HTTP 403 Access Denied | Status: 403 | **PASS** |
| **Case D** | `/admin` パスアクセス | HTTP 403 Forbidden | Status: 403 | **PASS** |
| **Case E** | Stats / LLM パスアクセス | HTTP 403 Forbidden | Status: 403 | **PASS** |
| **Case F** | 存在しない API パス大量要求 | 内部情報・スタックトレース非公開 | Status: 403 (エラーマスク適用) | **PASS** |
| **Case G** | 想定外パラメータ送信 | 500 Stack Trace 非露出 | Status: 422 (サニタイズ応答) | **PASS** |

---

## 5. T024 URL 障害状態 & モバイル実機確認

`worldnews_test.db` に含まれる T024 の 6 状態に対する UI 表示動作およびモバイル表示の適合性を実機レベルで確認完了しました。

- **ACTIVE / REDIRECTED**: `[ 元記事を読む ↗ ]` ボタンが正常動作。
- **NOT_FOUND / GONE**: `⚠ 元記事は削除・移動された可能性があります` 警告が表示されつつ、Article Preview と同一 Event 内の代替記事（Alternative Article）を提示し、ユーザーが行き止まりにならない UI を確保。
- **BLOCKED / TEMPORARY_UNAVAILABLE**: 一時的アクセス制限として扱い、死亡確定としない適切なメッセージを表示。

---

## 6. 最終結論

本環境は、Production Pi3/Pi4/SQLite/LLM から完全に切り離されており、外部テスター（友人）が安全かつ快適に体験できる状態であることを承認します。
