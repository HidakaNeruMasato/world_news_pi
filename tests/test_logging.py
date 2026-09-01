"""ロギング機能のユニットテスト"""

import logging
from world_news.logging import setup_logging


def test_setup_logging():
    """setup_logging が正常にロガーを返すか確認"""
    logger = setup_logging(level=logging.DEBUG)
    assert logger.name == "world_news"
    assert logger.level == logging.DEBUG
