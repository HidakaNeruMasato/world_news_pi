"""Friend Test API Application & Security Middleware Module (T025 friend_api.py)

外部テスター（友人）向け専用の Read-Only / 本番完全分離 API サーバー。
- 接続先: worldnews_test.db のみ限定
- 制限: GET のみ許可 (POST, PUT, PATCH, DELETE 拒否 405/403)
- 内部API遮断: /api/v1/internal/*, /api/dashboard/*, /api/v1/stats 遮断 (403)
- CORS 制限: GitHub Pages Origin のみ
- Rate Limiting: 60 req/min/client (429)
"""

import time
from typing import Dict, Tuple, Optional, Any, List
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from world_news.api.database import Pi4Database

DEFAULT_TEST_DB_PATH = "worldnews_test.db"

# 許可された CORS Origin (GitHub Pages 及び開発環境)
ALLOWED_ORIGINS = [
    "https://*.github.io",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

# 短時間インメモリキャッシュ (15s TTL)
_ACTIVE_EVENTS_CACHE: Dict[str, Tuple[float, dict]] = {}
CACHE_TTL_SECONDS = 15.0


class FriendTestSecurityMiddleware(BaseHTTPMiddleware):
    """外部ユーザーテスト用セキュリティミドルウェア"""

    def __init__(self, app: FastAPI, max_requests_per_minute: int = 60):
        super().__init__(app)
        self.max_requests_per_minute = max_requests_per_minute
        self._ip_request_history: Dict[str, List[float]] = {}

    def _is_rate_limited(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60.0
        timestamps = self._ip_request_history.get(client_ip, [])
        # 60秒以内のアクセスログを保持
        timestamps = [ts for ts in timestamps if ts >= window_start]
        if len(timestamps) >= self.max_requests_per_minute:
            return True
        timestamps.append(now)
        self._ip_request_history[client_ip] = timestamps
        return False

    async def dispatch(self, request: Request, call_next):
        # 1. HTTP Method 制限 (GET, OPTIONS のみ許可)
        if request.method not in ("GET", "OPTIONS", "HEAD"):
            return Response(
                content='{"detail": "Method Not Allowed in Read-Only Friend Test Environment"}',
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                media_type="application/json",
            )

        # 2. 内部 API・管理機能のアクセス遮断
        path = request.url.path.lower()
        if (
            "/api/v1/internal/" in path
            or "/api/dashboard/" in path
            or path.endswith("/stats")
            or "/admin" in path
            or "/link-check" in path
        ):
            return Response(
                content='{"detail": "Access Denied: Internal administrative endpoints are disabled in Friend Test Environment"}',
                status_code=status.HTTP_403_FORBIDDEN,
                media_type="application/json",
            )

        # 3. Rate Limiting (60 req/min/IP)
        client_ip = request.client.host if request.client else "unknown"
        if self._is_rate_limited(client_ip):
            return Response(
                content='{"detail": "Too Many Requests: Rate limit exceeded (60 req/min). Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
            )

        # 4. サニタイズ例外ハンドリング
        try:
            response = await call_next(request)
            return response
        except Exception:
            return Response(
                content='{"detail": "Unable to retrieve news information. Please try again later."}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="application/json",
            )


def create_friend_app(db_path: str = DEFAULT_TEST_DB_PATH) -> FastAPI:
    """Friend Test 専用 Read-Only FastAPI アプリケーション作成」"""
    test_db = Pi4Database(db_path=db_path)

    friend_app = FastAPI(
        title="World News Map Friend Test API (Read-Only)",
        description="外部テスター（友人）向け本番完全分離 Read-Only API サーバー",
        version="0.2.5",
        docs_url=None,  # 内部ドキュメント非公開
        redoc_url=None,
    )

    friend_app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https://.*\.github\.io|http://(localhost|127\.0\.0\.1):(5173|3000)",
        allow_credentials=True,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["*"],
    )

    friend_app.add_middleware(FriendTestSecurityMiddleware, max_requests_per_minute=60)

    @friend_app.get("/api/v1/health")
    @friend_app.get("/api/health")
    def get_friend_health():
        """サニタイズされたヘルスチェック"""
        return {
            "status": "ok",
            "environment": "friend_test_readonly",
            "database": "connected",
        }

    @friend_app.get("/api/events/active")
    @friend_app.get("/api/v1/events/active")
    def get_active_events(min_confidence: float = 0.50, limit: int = 100):
        """アクティブイベント一覧の取得 (15s キャッシュ)"""
        cache_key = f"{min_confidence}_{limit}"
        now = time.time()
        if cache_key in _ACTIVE_EVENTS_CACHE:
            ts, cached_data = _ACTIVE_EVENTS_CACHE[cache_key]
            if now - ts < CACHE_TTL_SECONDS:
                return cached_data

        events = test_db.get_active_events(min_confidence=min_confidence, limit=limit)
        normalized_events = []
        for evt in events:
            normalized_events.append({
                "id": evt["id"],
                "category": evt["event_type"],
                "event_country": evt["country_code"],
                "country_name": evt.get("country_name"),
                "region": evt.get("region"),
                "city": evt.get("city"),
                "location_name": evt.get("location_name"),
                "latitude": evt["latitude"],
                "longitude": evt["longitude"],
                "confidence": evt["confidence"],
                "status": evt["status"],
                "geocoding_status": evt["geocoding_status"],
                "occurred_at": evt.get("event_time") or evt.get("first_seen_at"),
                "detected_at": evt.get("first_seen_at"),
                "last_seen_at": evt.get("last_seen_at"),
                "expires_at": evt.get("expires_at"),
            })

        res_data = {
            "events": normalized_events,
            "count": len(normalized_events),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        _ACTIVE_EVENTS_CACHE[cache_key] = (now, res_data)
        return res_data

    @friend_app.get("/api/events/{event_id}/articles")
    @friend_app.get("/api/v1/events/{event_id}/articles")
    def get_event_articles(event_id: int):
        """指定イベントに関連付けられたニュース記事一覧を取得します"""
        articles = test_db.get_event_articles(event_id)
        return {"articles": articles, "count": len(articles)}

    @friend_app.get("/api/v1/events/{event_id}/reachability")
    def get_event_reachability(event_id: int):
        """指定イベントの Reachability を取得します"""
        return test_db.get_event_reachability(event_id)

    return friend_app
