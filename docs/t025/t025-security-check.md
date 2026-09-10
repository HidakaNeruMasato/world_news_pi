# T025 セキュリティ検証レポート (docs/t025/t025-security-check.md)

## 1. 概要

本レポートは、T025 外部ユーザーテスト環境におけるセキュリティ保護および本番環境分離の判定結果を記録したものです。

---

## 2. セキュリティチェックリスト (Acceptance Criteria Security 15項目)

| No | セキュリティ項目 | 結果 | 判定基準・根拠 |
|----|------------------|------|----------------|
| 1  | Production DB が外部公開されていないか | **PASS** | Friend Test API は `worldnews_test.db` のみに接続し、`worldnews.db` へのアクセス経路を持たない |
| 2  | Production API が外部公開されていないか | **PASS** | 本番 API (port 8080) は LAN 内閉塞で運用され、外部には `Friend Test API` のみが到達可能 |
| 3  | Pi3 SSH が外部公開されていないか | **PASS** | SSH (Port 22) はルーターおよびファイアウォールで外部遮断 |
| 4  | Pi4 SSH が外部公開されていないか | **PASS** | SSH (Port 22) はルーターおよびファイアウォールで外部遮断 |
| 5  | LLM endpoint が外部公開されていないか | **PASS** | `llama-server` (Port 8081) は localhost/LAN 内閉塞 |
| 6  | Link Checker 任意 URL API が存在しないか | **PASS** | SSRF 防止のため `POST /api/link-check` 等の任意 URL 受け入れ API を非搭載 |
| 7  | POST/PUT/PATCH/DELETE を友人が実行できないか | **PASS** | `FriendTestSecurityMiddleware` により GET 以外の書き込み系メソッドは全て `405 Method Not Allowed` で拒否 |
| 8  | Internal API へ外部から到達できないか | **PASS** | `/api/v1/internal/*`, `/api/dashboard/*`, `/api/v1/stats` へのアクセスは `403 Forbidden` で全遮断 |
| 9  | Production credentials が Web Bundle にないか | **PASS** | `VITE_API_BASE_URL` のみを使用し、LAN IP (`192.168.0.x`) や本番シークレットは非混入 |
| 10 | GitHub Repository に secret がないか | **PASS** | Git 全コミット履歴のシークレットスキャン (`git log --all -S"API_KEY"`) を実施し、検出 0件 |
| 11 | Test API は Test DB だけを使用しているか | **PASS** | `Pi4Database(db_path="worldnews_test.db")` に固着 |
| 12 | Test API から Production DB へ到達できないか | **PASS** | ソースコード上に `worldnews.db` へのフォールバック処理なし |
| 13 | CORS が限定されているか | **PASS** | 許可 Origin を GitHub Pages (`*.github.io`) および開発 Origin に限定（`*` 許可なし） |
| 14 | HTTPS で通信されているか | **PASS** | GitHub Pages および Friend Test API 通信は HTTPS のみ |
| 15 | Rate Limit が設定されているか | **PASS** | IP 単位で 60 req/min に制限（超過時 `429 Too Many Requests`） |

---

## 3. Git シークレットスキャン結果

```bash
git log --all -S"API_KEY"
git log --all -S"PASSWORD"
git log --all -S"TOKEN"
```
- **検出件数**: 0件（秘密情報・認証トークン・SSH鍵の過去履歴混入なし）
