# T024 URL Status Model Specification

## 1. Overview

World News Map の T024 において導入された Article URL 状態モデル (`url_status`) および URL 3層モデルの仕様です。

外部ニュースサイトの URL 変更、記事削除、一時障害、リダイレクト、アクセス制限を正確に分類し、イベント表示の健全性とユーザーのニュース到達可能性（Event Reachability）を保護します。

---

## 2. URL 3層モデル

* **`original_url`**: RSSコレクターが収集時に取得した不変の初期 URL (例: `https://news.example.com/old/123`)
* **`canonical_url`**: HTML から抽出された代表 URL (`<link rel="canonical" href="...">`)
* **`current_url`**: 現在ユーザーに提示される最新の有効アクセス URL (デフォルト: `final_url` → `canonical_url` → `original_url`)

---

## 3. URL 状態定義 (`url_status`)

| Status | HTTP Code / 条件 | 概要 | ユーザー提示 UI |
|---|---|---|---|
| **`unknown`** | 未検証 | まだリンクチェックが実行されていない | 🟢 **元記事を読む ↗** |
| **`active`** | HTTP 200 (かつ Soft 404 でない) | 正常に記事が存在 | 🟢 **元記事を読む ↗** |
| **`redirected`** | HTTP 3xx リダイレクト追跡後 200 | URLが更新・移転されたが有効 | 🟢 **元記事を読む ↗** <br>*(※ リンク先URLが更新されています)* |
| **`not_found`** | HTTP 404 または Soft 404 | 記事が存在しない / 削除 | ⚠ **元記事は現在確認できません (移動または削除)** <br>*(※ 代替記事導線を提示)* |
| **`gone`** | HTTP 410 | 恒久的に削除された | ⚠ **元記事は現在確認できません (移動または削除)** |
| **`blocked`** | HTTP 403 / 429 | アクセス制限 / botブロック | ⚠ **元記事を確認できません (アクセス制限・一時障害)** |
| **`temporary_unavailable`** | HTTP 5xx | 一時的なサーバー障害 | ⚠ **元記事を確認できません (アクセス制限・一時障害)** |
| **`timeout`** | 接続・応答タイムアウト | 10秒応答なし | ⚠ **元記事を確認できません (アクセス制限・一時障害)** |
| **`invalid`** | Scheme 不正 / Redirect loop | 不正なURL形式 | ⚠ **元記事URLを取得できません** |

---

## 4. URL 変更履歴記録 (`article_url_history`)

`articles` テーブルの `current_url` または `url_status` に変更が生じた場合、アトミックに `article_url_history` テーブルへ変更履歴が挿入され、追跡可能になります。
