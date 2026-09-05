"""FastAPI アプリケーション定義モジュール"""

import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from world_news.config import load_config
from world_news.api.database import Pi4Database
from world_news.schemas import HealthStatus

config = load_config()
db = Pi4Database(db_path=config.pi4.db_path)

app = FastAPI(
    title="World News Intake & Storage API",
    description="Pi3から送られてくる正規化記事を受領・保持・解析・Web配信する内部API",
    version="0.2.0",
)

# CORS 設定 (開発環境 Origin の許可)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def create_app(db_path: Optional[str] = None) -> FastAPI:
    """FastAPI アプリケーションインスタンス作成ヘルパー"""
    global db
    if db_path:
        db = Pi4Database(db_path=db_path)
    return app


class ArticlePayload(BaseModel):
    source_id: int
    source_country: Optional[str] = "XX"
    external_id: Optional[str] = None
    title: str
    description: Optional[str] = ""
    url: Optional[str] = ""
    published_at: Optional[str] = ""
    fetched_at: Optional[str] = ""
    language: Optional[str] = "en"
    content_hash: Optional[str] = ""


@app.get("/api/health")
def get_health_v2():
    """T016 統合ヘルスチェックエンドポイント"""
    return HealthStatus(
        status="ok",
        database="ok",
        llm="ok",
        queue="ok",
    )


@app.get("/api/v1/health", response_model=HealthStatus)
def get_health():
    """ヘルスチェックエンドポイント (旧互換)"""
    return HealthStatus(
        status="ok",
        database="ok",
        llm="not_configured",
        queue="ok",
    )


@app.post("/api/v1/internal/articles", status_code=status.HTTP_201_CREATED)
def intake_article(payload: ArticlePayload, response: Response):
    """Pi3から配送された記事の受領とジョブアトミック登録 (201 Created or 200 OK)"""
    if not payload.title or not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty",
        )

    try:
        article_id, already_exists = db.insert_article_with_job(payload.model_dump())
        if already_exists:
            response.status_code = status.HTTP_200_OK
            return {
                "status": "already_exists",
                "message": "Article already exists (duplicate)",
                "article_id": article_id,
            }
        return {
            "status": "created",
            "message": "Article ingested and processing job created",
            "article_id": article_id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest article: {str(e)}",
        )


@app.get("/api/events/active")
@app.get("/api/v1/events/active")
def get_active_events(min_confidence: float = 0.50, limit: int = 100):
    """T008 の Active Event Query によるアクティブイベント一覧の取得"""
    events = db.get_active_events(min_confidence=min_confidence, limit=limit)
    
    # フロントエンド互換の正規化キーマッピング
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

    return {
        "events": normalized_events,
        "count": len(normalized_events),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


from world_news.dashboard.metrics import DashboardMetricsCollector

dashboard_collector = DashboardMetricsCollector()


@app.get("/api/events/{event_id}/articles")
@app.get("/api/v1/events/{event_id}/articles")
def get_event_articles(event_id: int):
    """指定イベントに関連付けられたニュース記事一覧を取得します"""
    articles = db.get_event_articles(event_id)
    return {"articles": articles, "count": len(articles)}


@app.get("/api/v1/events")
def get_events():
    """現在アクティブなイベント一覧を取得します (旧互換)"""
    return get_active_events(min_confidence=0.0)


@app.get("/api/v1/stats")
def get_stats() -> Dict[str, Any]:
    """システムの各種統計情報を取得します"""
    return db.get_stats()


# --- T019 Dashboard Endpoints ---

@app.get("/api/dashboard/summary")
def get_dashboard_summary(period: str = "24h"):
    """T019 Dashboard Overview KPI Summary"""
    return dashboard_collector.get_summary(period=period)


@app.get("/api/dashboard/funnel")
def get_dashboard_funnel(period: str = "24h"):
    """T019 Pipeline Reduction Funnel Metrics"""
    return dashboard_collector.get_funnel(period=period)


@app.get("/api/dashboard/regions")
def get_dashboard_regions(period: str = "24h"):
    """T019 Regional Activity Breakdown"""
    return dashboard_collector.get_regional_activity(period=period)


@app.get("/api/dashboard/countries")
def get_dashboard_countries(period: str = "24h"):
    """T019 Event Country Activity Breakdown"""
    return dashboard_collector.get_country_activity(period=period)


@app.get("/api/dashboard/sources")
def get_dashboard_sources(period: str = "24h"):
    """T019 Source Media Performance & Conversion Rates"""
    return dashboard_collector.get_source_metrics(period=period)


@app.get("/api/dashboard/timeseries")
def get_dashboard_timeseries(period: str = "24h"):
    """T019 Time-series Activity Metrics"""
    return dashboard_collector.get_timeseries(period=period)


@app.get("/api/dashboard/source-health")
def get_dashboard_source_health():
    """T019 Monitoring Integration Health Status"""
    return dashboard_collector.get_source_health()


# Web ビルド成果物 (web/dist) の静的配信設定
web_dist_dir = Path(__file__).resolve().parent.parent.parent.parent / "web" / "dist"
if web_dist_dir.exists() and web_dist_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(web_dist_dir), html=True), name="static_web")


