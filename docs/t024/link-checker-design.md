# T024 Article Link Checker Architecture & Design

## 1. System Architecture

`ArticleLinkChecker` は、外部ニュースサーバーの負荷やアクセス制御に配慮しつつ、非同期/並列で記事 URL の状態を検証する独立モジュールです。

```text
Article URL
     ↓
Scheme Validation (is_safe_url)
     ↓
Host Throttling (5s interval / host)
     ↓
HTTP GET Request (User-Agent: WorldNewsMap-LinkChecker/1.0, timeout 10s)
     ↓
Redirect Follow (Max 5 redirects)
     ↓
HTML Parse (<link rel="canonical"> & <title>)
     ↓
Soft 404 Detection
     ↓
Result Mapping & Database Update
```

---

## 2. Throttling & Raspberry Pi 4 Optimization

* **User-Agent**: `WorldNewsMap-LinkChecker/1.0 (+https://github.com/world-news-map)`
* **Concurrency**: `2` workers max
* **Host Throttling**: 同一ホストドメインに対して最低 `5.0秒` のインターバルを自動適用
* **Timeout**: 接続・応答タイムアウト `10.0秒`

---

## 3. Alternative Articles Fallback Logic

記事の `url_status` が `not_found` または `gone` と判定された場合、同一 `event_id` に紐付く他メディアの `active` または `redirected` な記事を自動抽出し、ユーザーへ「このイベントを報じている他のニュースソース (Alternative Articles)」として優先案内します。
これにより、特定の元記事が削除された場合でもイベント全体の到達可能性（Event Reachability Rate）は 100% 維持されます。
