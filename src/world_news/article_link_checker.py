"""Article Link Reliability & Checker Module (T024 article_link_checker.py)

ニュース記事の外部 URL に対するリンク健全性確認・リダイレクト追跡・カノニカル URL 検出エンジン。
"""

import re
import time
import urllib.request
import urllib.error
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple, List
from html.parser import HTMLParser


USER_AGENT = "WorldNewsMap-LinkChecker/1.0 (+https://github.com/world-news-map)"
MAX_REDIRECTS = 5
DEFAULT_TIMEOUT_SECONDS = 10.0
MIN_HOST_INTERVAL_SECONDS = 5.0

SOFT_404_TITLE_PATTERNS = [
    r"404\s+not\s+found",
    r"page\s+not\s+found",
    r"article\s+not\s+found",
    r"記事が見つかりません",
    r"ページが見つかりません",
    r"お探しのページは",
    r"404\s+エラー",
    r"page\s+unavailable",
    r"error\s+404",
]


@dataclass
class ArticleLinkCheckResult:
    original_url: str
    final_url: str
    canonical_url: Optional[str] = None
    http_status: Optional[int] = None
    status: str = "unknown"  # active, redirected, not_found, gone, temporary_unavailable, blocked, timeout, invalid
    redirect_count: int = 0
    title: Optional[str] = None
    checked_at: Optional[str] = None
    error: Optional[str] = None


class CanonicalAndTitleParser(HTMLParser):
    """HTML から <link rel="canonical"> および <title> を抽出するパーサー"""

    def __init__(self):
        super().__init__()
        self.canonical_url: Optional[str] = None
        self.title: Optional[str] = None
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list):
        tag_lower = tag.lower()
        attr_dict = {k.lower(): v for k, v in attrs if k}

        if tag_lower == "link":
            rel = attr_dict.get("rel", "").lower()
            href = attr_dict.get("href")
            if rel == "canonical" and href:
                self.canonical_url = href.strip()

        elif tag_lower == "title":
            self._in_title = True

    def handle_endtag(self, tag: str):
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str):
        if self._in_title and data:
            if not self.title:
                self.title = data.strip()
            else:
                self.title += " " + data.strip()


class ArticleLinkChecker:
    """記事 URL の生存・リダイレクト・カノニカル検証クラス"""

    def __init__(self, min_host_interval: float = MIN_HOST_INTERVAL_SECONDS):
        self.min_host_interval = min_host_interval
        self._last_host_access: Dict[str, float] = {}

    def _throttle_host(self, url: str):
        """同一ホストに対するアクセス間隔制限 (Host Rate Limiting)"""
        try:
            parsed = urllib.parse.urlparse(url)
            host = parsed.netloc.lower()
            if not host:
                return
            now = time.time()
            last_access = self._last_host_access.get(host, 0.0)
            elapsed = now - last_access
            if elapsed < self.min_host_interval:
                sleep_time = self.min_host_interval - elapsed
                time.sleep(sleep_time)
            self._last_host_access[host] = time.time()
        except Exception:
            pass

    def is_safe_url(self, url: str) -> bool:
        """URL が安全な http/https スキーマか判定"""
        if not url or not isinstance(url, str):
            return False
        try:
            parsed = urllib.parse.urlparse(url.strip())
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False

    def check_url(self, url: str, max_redirects: int = MAX_REDIRECTS, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> ArticleLinkCheckResult:
        """記事 URL のリンク状態を検証"""
        now_str = datetime.now(timezone.utc).isoformat()

        if not self.is_safe_url(url):
            return ArticleLinkCheckResult(
                original_url=url,
                final_url=url,
                status="invalid",
                checked_at=now_str,
                error="Invalid HTTP/HTTPS URL scheme",
            )

        self._throttle_host(url)

        current_target = url.strip()
        redirect_count = 0
        visited_urls = {current_target}

        req_headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        while redirect_count <= max_redirects:
            try:
                req = urllib.request.Request(current_target, headers=req_headers, method="GET")

                # カスタムリダイレクトハンドラークラスで個別に追跡
                class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
                    def redirect_request(self, req, fp, code, msg, headers, newurl):
                        return None

                opener = urllib.request.build_opener(NoRedirectHandler)
                with opener.open(req, timeout=timeout) as response:
                    status_code = response.status
                    content_type = response.headers.get("Content-Type", "").lower()
                    raw_body = response.read(1024 * 256)  # 先頭 256KB のみ取得

                    # HTML 解析で canonical URL と title を取得
                    canonical_url, title = self._parse_html(current_target, raw_body, content_type)

                    # Soft 404 判定
                    is_soft_404 = self._check_soft_404(title, raw_body.decode("utf-8", errors="ignore"))

                    final_status = "active"
                    if is_soft_404:
                        final_status = "not_found"
                    elif current_target != url:
                        final_status = "redirected"

                    return ArticleLinkCheckResult(
                        original_url=url,
                        final_url=current_target,
                        canonical_url=canonical_url,
                        http_status=status_code,
                        status=final_status,
                        redirect_count=redirect_count,
                        title=title,
                        checked_at=now_str,
                    )

            except urllib.error.HTTPError as e:
                status_code = e.code
                if status_code in (301, 302, 303, 307, 308):
                    location = e.headers.get("Location")
                    if not location:
                        return ArticleLinkCheckResult(
                            original_url=url,
                            final_url=current_target,
                            http_status=status_code,
                            status="invalid",
                            redirect_count=redirect_count,
                            checked_at=now_str,
                            error="HTTP redirect without Location header",
                        )

                    next_url = urllib.parse.urljoin(current_target, location.strip())
                    if next_url in visited_urls:
                        return ArticleLinkCheckResult(
                            original_url=url,
                            final_url=next_url,
                            http_status=status_code,
                            status="invalid",
                            redirect_count=redirect_count + 1,
                            checked_at=now_str,
                            error="Redirect loop detected",
                        )

                    visited_urls.add(next_url)
                    current_target = next_url
                    redirect_count += 1
                    continue

                # HTTP エラーコード別のステータス判定
                if status_code == 404:
                    status_label = "not_found"
                elif status_code == 410:
                    status_label = "gone"
                elif status_code in (403, 429):
                    status_label = "blocked"
                elif status_code >= 500:
                    status_label = "temporary_unavailable"
                else:
                    status_label = "temporary_unavailable"

                return ArticleLinkCheckResult(
                    original_url=url,
                    final_url=current_target,
                    http_status=status_code,
                    status=status_label,
                    redirect_count=redirect_count,
                    checked_at=now_str,
                    error=f"HTTP {status_code}",
                )

            except (urllib.error.URLError, TimeoutError) as e:
                err_str = str(e)
                if "timed out" in err_str.lower() or isinstance(e, TimeoutError):
                    status_label = "timeout"
                else:
                    status_label = "temporary_unavailable"

                return ArticleLinkCheckResult(
                    original_url=url,
                    final_url=current_target,
                    status=status_label,
                    redirect_count=redirect_count,
                    checked_at=now_str,
                    error=err_str,
                )

            except Exception as e:
                return ArticleLinkCheckResult(
                    original_url=url,
                    final_url=current_target,
                    status="temporary_unavailable",
                    redirect_count=redirect_count,
                    checked_at=now_str,
                    error=str(e),
                )

        # リダイレクト回数超過
        return ArticleLinkCheckResult(
            original_url=url,
            final_url=current_target,
            status="invalid",
            redirect_count=redirect_count,
            checked_at=now_str,
            error=f"Exceeded maximum redirects ({max_redirects})",
        )

    def _parse_html(self, base_url: str, body_bytes: bytes, content_type: str) -> Tuple[Optional[str], Optional[str]]:
        """HTML から canonical URL および title を抽出"""
        if "html" not in content_type and not body_bytes.startswith(b"<!") and not b"<html" in body_bytes.lower():
            return None, None

        try:
            html_str = body_bytes.decode("utf-8", errors="ignore")
            parser = CanonicalAndTitleParser()
            parser.feed(html_str[:100000])  # 先頭 100KB のみ解析

            canonical = None
            if parser.canonical_url:
                c_url = urllib.parse.urljoin(base_url, parser.canonical_url.strip())
                if self.is_safe_url(c_url):
                    canonical = c_url

            return canonical, parser.title
        except Exception:
            return None, None

    def _check_soft_404(self, title: Optional[str], body_text: str) -> bool:
        """タイトルおよび本文に基づく Soft 404 判定"""
        if title:
            title_lower = title.lower()
            for pattern in SOFT_404_TITLE_PATTERNS:
                if re.search(pattern, title_lower):
                    return True

        return False
