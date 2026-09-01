"""FastAPI Web アプリケーション: Pi4 REST API エンドポイント"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field, field_validator
from world_news.config import load_config
from world_news.api.database import Pi4Database


class ArticleIntakeRequest(BaseModel):
    """Pi3 から送信される受領用リクエストモデル"""
    source_id: int
    source_country: Optional[str] = "XX"
    external_id: Optional[str] = None
    title: str = Field(..., min_length=1, description="記事タイトル (必須・空不可)")
    description: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[str] = None
    fetched_at: Optional[str] = None
    language: Optional[str] = None
    content_hash: Optional[str] = None

    @field_validator("title")

    def validate_title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title must not be empty or whitespace only")
        return v.strip()


def create_app(db_path: Optional[str] = None) -> FastAPI:
    config = load_config()
    db = Pi4Database(db_path=db_path or "worldnews.db")

    app = FastAPI(
        title="World News Event Map API",
        version="0.1.0",
        description="Pi4 Canonical REST API",
    )

    @app.get("/api/v1/health")
    def get_health():
        """システムヘルスチェック。LLM は未実装のため 'not_configured' を返します。"""
        try:
            db.get_stats()
            db_status = "ok"
        except Exception:
            db_status = "error"

        return {
            "status": "ok" if db_status == "ok" else "degraded",
            "database": db_status,
            "queue": "ok",
            "llm": "not_configured",
        }

    @app.post("/api/v1/internal/articles", status_code=status.HTTP_201_CREATED)
    def intake_article(req: ArticleIntakeRequest, response: Response):
        """Pi3 からの正規化ニュース記事受領内部 API (At-Least-Once / ACK 冪等対応)"""
        payload = req.model_dump()

        try:
            article_id, already_exists = db.insert_article_with_job(payload)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database transaction failure: {str(e)}",
            )

        if already_exists:
            # 重複受領時は 200 OK ACK を返却して Pi3 が送信完了と認識できるようにする
            response.status_code = status.HTTP_200_OK
            return {
                "status": "already_exists",
                "article_id": article_id,
                "message": "Article already exists, ACK acknowledged",
            }

        return {
            "status": "created",
            "article_id": article_id,
            "message": "Article ingested and processing job created",
        }

    @app.get("/api/v1/events")
    def get_events():
        """アクティブイベント一覧 (T004 時点では 0 件)"""
        return {
            "events": [],
            "count": 0,
        }

    @app.get("/api/v1/stats")
    def get_stats():
        """システム統計情報"""
        return db.get_stats()

    return app


app = create_app()
