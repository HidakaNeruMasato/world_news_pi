# T025-1 ネットワーク境界 & セキュリティ設定検証報告書 (Network Boundary Check)

## 1. 概要

本ドキュメントは、World News Map 外部ユーザーテスト環境における **ネットワーク境界線、ポート遮断状況、暗号化 (HTTPS)、CORS 設定、および Rate Limiting** に関する技術検証結果をまとめたものです。

---

## 2. ネットワークトポロジーと境界線

```text
                                [ Internet (外部網) ]
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │                                             │
                   ▼ (HTTPS)                                     ▼ (HTTPS)
      ┌─────────────────────────┐                   ┌─────────────────────────┐
      │   GitHub Pages (Web UI) │                   │  Friend Test API Server │
      │   https://<user>.github.io│                   │  (Port 443 / Read-Only) │
      └─────────────────────────┘                   └────────────┬────────────┘
                                                                 │ (ローカル)
                                                                 ▼
                                                    ┌─────────────────────────┐
                                                    │   worldnews_test.db     │
                                                    └─────────────────────────┘

 ═══════════════════════════ 物理 & 論理セキュリティ境界線 ═══════════════════════════

                               [ LAN 内 (外部非公開網) ]
      ┌───────────────────────────────────────────────────────────────────────┐
      │  Production Pi3 / Pi4 インフラ                                        │
      │   - Production API (Port 8080)   : 到達不可 (Blocked / Refused)       │
      │   - SSH Daemon (Port 22)         : 到達不可 (Blocked / Refused)       │
      │   - llama-server (Port 8081)     : 到達不可 (Blocked / Refused)       │
      │   - Production DB worldnews.db   : 直接参照ルートなし                   │
      └───────────────────────────────────────────────────────────────────────┘
```

---

## 3. 外部ポート非公開検証 (Port Accessibility Scan)

外部回線（4G/5G 回線および外部スキャンツール）から Production IP およびドメインに対して、主要ポートの疎通確認を実施しました。

| 対象コンポーネント | ポート番号 | 期待結果 | 外部回線スキャン結果 | 判定 |
|---|---|---|---|---|
| Production API | TCP/8080 | Connection Refused / Timeout | 到達不能 (Unreachable) | **PASS** |
| Pi3 / Pi4 SSH | TCP/22 | Connection Refused / Timeout | 到達不能 (Unreachable) | **PASS** |
| llama-server (LLM) | TCP/8081 | Connection Refused / Timeout | 到達不能 (Unreachable) | **PASS** |
| Friend Test API | TCP/443 (HTTPS) | HTTP 200 OK | アクセス可能 | **PASS** |

> [!IMPORTANT]
> **ルーター Port Forwarding 設定の検証**
> ルーター側で 8080, 22, 8081 へのポート転送（Port Forwarding）が一切設定されていないことを確認済み。プライベート IP 帯（`192.168.0.x`）は Internet 上で非ルーティングアドレスであるため、外部から直叩きすることはできません。

---

## 4. HTTPS 暗号化 & CORS ポリシー検証

### 4-1. HTTPS 暗号化
- Web UI (GitHub Pages) および Friend Test API は全通信が TLS/HTTPS で暗号化されています。
- 非暗号化 HTTP 通信は拒否または自動リダイレクトされます。

### 4-2. CORS (Cross-Origin Resource Sharing) 制限
- ワイルドカード `Access-Control-Allow-Origin: *` は使用されていません。
- 許可される Origin は以下の正規パターンに限定されています:
  - `https://*.github.io` (GitHub Pages ホスティング環境)
  - `http://localhost:5173`, `http://127.0.0.1:5173` (ローカル検証用)

```python
# friend_api.py での制限定義
friend_app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.github\.io|http://(localhost|127\.0\.0\.1):(5173|3000)",
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)
```

---

## 5. Rate Limiting & Proxy IP 追跡方針

### 5-1. Rate Limiting 仕様
- **制限閾値**: 60 requests / 分 / クライアント IP
- **制御ロジック**: `FriendTestSecurityMiddleware` によりインメモリ追跡。制限超過時は即座に `429 Too Many Requests` を返却。

### 5-2. リバースプロキシ / Forwarded IP の扱い
- Friend API が Cloudflare や Nginx 等のリバースプロキシ背後に配置される場合、`request.client.host` がプロキシの IP に固定されるリスクを防ぐため、信頼できるヘッダー（`X-Forwarded-For`）のサニタイズ処理を考慮した設計となっています。
- 現行テスト環境では単体レスポンス制御により、誤遮断なく 60 req/min が正常機能することを確認しました。
