"""HTTP フェッチャーモジュール: HTTP/HTTPS リクエストの実行と条件付き取得"""

import urllib.request
import urllib.error
import socket
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class FetchResult:
    """HTTP 取得結果オブジェクト"""
    content: Optional[bytes]
    status_code: int
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    error_message: Optional[str] = None
    not_modified: bool = False


class FeedFetcher:
    """フィード取得を担当するクラス"""

    USER_AGENT = "WorldNewsCollector/1.0 (+http://worldnews.local)"

    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    def fetch(
        self,
        url: str,
        etag: Optional[str] = None,
        last_modified: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> FetchResult:
        """指定された URL からフィードコンテンツを取得します。

        conditional request (If-None-Match, If-Modified-Since) をサポートします。
        """
        req_timeout = timeout or self.timeout
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
        }

        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified

        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=req_timeout) as response:
                status_code = response.getcode()
                res_etag = response.headers.get("ETag")
                res_last_modified = response.headers.get("Last-Modified")
                content = response.read()

                return FetchResult(
                    content=content,
                    status_code=status_code,
                    etag=res_etag,
                    last_modified=res_last_modified,
                )

        except urllib.error.HTTPError as e:
            if e.code == 304:
                return FetchResult(
                    content=None,
                    status_code=304,
                    etag=etag,
                    last_modified=last_modified,
                    not_modified=True,
                )
            return FetchResult(
                content=None,
                status_code=e.code,
                error_message=f"HTTP Error {e.code}: {e.reason}",
            )

        except urllib.error.URLError as e:
            msg = str(e.reason)
            if isinstance(e.reason, socket.timeout):
                msg = "HTTP Timeout"
            return FetchResult(
                content=None,
                status_code=0,
                error_message=f"URL Error: {msg}",
            )

        except socket.timeout:
            return FetchResult(
                content=None,
                status_code=0,
                error_message="HTTP Timeout",
            )

        except Exception as e:
            return FetchResult(
                content=None,
                status_code=0,
                error_message=f"Unexpected error: {str(e)}",
            )
