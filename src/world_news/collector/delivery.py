"""Pi4 配送モジュール: Pi4 REST API への記事送信と ACK 確認"""

import json
import urllib.request
import urllib.error
import socket
from typing import List, Dict, Tuple, Optional


class DeliveryResult:
    """配送試行結果"""
    def __init__(self, success_ids: List[int], failed_items: List[Tuple[int, str]]):
        self.success_ids = success_ids
        self.failed_items = failed_items  # [(article_id, error_message)]


class Pi4DeliveryClient:
    """Pi4 内部 API (POST /api/v1/internal/articles) へ記事を送信するクライアント"""

    def __init__(self, submit_url: str = "http://worldnews-pi4:8080/api/v1/internal/articles", timeout: int = 10):
        self.submit_url = submit_url
        self.timeout = timeout

    def deliver_article(self, article: dict) -> Tuple[bool, Optional[str]]:
        """1件の記事を Pi4 に配送し、ACK (200/201) の結果を返します"""
        payload = {
            "source_id": article["source_id"],
            "source_country": article.get("source_country", "XX"),
            "external_id": article["external_id"],
            "title": article["title"],
            "description": article.get("description"),
            "url": article.get("url"),
            "published_at": article.get("published_at"),
            "fetched_at": article.get("fetched_at"),
            "language": article.get("language"),
            "content_hash": article.get("content_hash"),
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.submit_url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "WorldNewsCollector/1.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                status = response.getcode()
                if status in (200, 201):
                    return True, None
                else:
                    return False, f"Unexpected HTTP status {status}"

        except urllib.error.HTTPError as e:
            return False, f"HTTP Error {e.code}: {e.reason}"

        except urllib.error.URLError as e:
            msg = str(e.reason)
            if isinstance(e.reason, socket.timeout):
                msg = "Connection timeout"
            return False, f"URL Error: {msg}"

        except socket.timeout:
            return False, "Connection timeout"

        except Exception as e:
            return False, f"Delivery error: {str(e)}"

    def deliver_batch(self, articles: List[dict]) -> DeliveryResult:
        """複数件の記事を一括または順次配送"""
        success_ids: List[int] = []
        failed_items: List[Tuple[int, str]] = []

        for article in articles:
            article_id = article["id"]
            ok, err = self.deliver_article(article)
            if ok:
                success_ids.append(article_id)
            else:
                failed_items.append((article_id, err or "Unknown error"))

        return DeliveryResult(success_ids, failed_items)
