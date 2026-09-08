"""Unit tests for ArticleLinkChecker (tests/test_article_link_checker.py)"""

import pytest
from world_news.article_link_checker import ArticleLinkChecker, ArticleLinkCheckResult, CanonicalAndTitleParser


def test_is_safe_url():
    checker = ArticleLinkChecker(min_host_interval=0.0)
    assert checker.is_safe_url("https://example.com/article/1") is True
    assert checker.is_safe_url("http://news.org") is True
    assert checker.is_safe_url("javascript:alert(1)") is False
    assert checker.is_safe_url("data:text/html,abc") is False
    assert checker.is_safe_url("") is False
    assert checker.is_safe_url(None) is False


def test_invalid_url_scheme_handling():
    checker = ArticleLinkChecker(min_host_interval=0.0)
    res = checker.check_url("ftp://example.com/file")
    assert res.status == "invalid"
    assert res.error == "Invalid HTTP/HTTPS URL scheme"


def test_canonical_and_title_parser():
    parser = CanonicalAndTitleParser()
    html_content = """
    <html>
      <head>
        <title>Sample News Title - BBC News</title>
        <link rel="canonical" href="https://www.bbc.com/news/world-123456" />
      </head>
      <body>Article Content</body>
    </html>
    """
    parser.feed(html_content)
    assert parser.title == "Sample News Title - BBC News"
    assert parser.canonical_url == "https://www.bbc.com/news/world-123456"


def test_soft_404_detection():
    checker = ArticleLinkChecker(min_host_interval=0.0)
    assert checker._check_soft_404("Page Not Found - 404", "Body content") is True
    assert checker._check_soft_404("記事が見つかりません - NHK", "Body content") is True
    assert checker._check_soft_404("Tokyo Stock Exchange Rises 2%", "Body content") is False


def test_live_check_url_200_active():
    checker = ArticleLinkChecker(min_host_interval=0.0)
    res = checker.check_url("https://httpbin.org/status/200")
    assert res.status in ("active", "redirected")
    assert res.http_status == 200


def test_live_check_url_404_not_found():
    checker = ArticleLinkChecker(min_host_interval=0.0)
    res = checker.check_url("https://httpbin.org/status/404")
    assert res.status == "not_found"
    assert res.http_status == 404


def test_live_check_url_410_gone():
    checker = ArticleLinkChecker(min_host_interval=0.0)
    res = checker.check_url("https://httpbin.org/status/410")
    assert res.status == "gone"
    assert res.http_status == 410


def test_live_check_url_403_blocked():
    checker = ArticleLinkChecker(min_host_interval=0.0)
    res = checker.check_url("https://httpbin.org/status/403")
    assert res.status == "blocked"
    assert res.http_status == 403


def test_live_check_url_500_temporary_unavailable():
    checker = ArticleLinkChecker(min_host_interval=0.0)
    res = checker.check_url("https://httpbin.org/status/500")
    assert res.status == "temporary_unavailable"
    assert res.http_status == 500
