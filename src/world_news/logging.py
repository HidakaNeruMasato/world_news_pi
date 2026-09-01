"""ロギング共通設定"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """システム共通のロギング初期化を設定します。

    Args:
        level: ログレベル (default: logging.INFO)
        log_format: ログフォーマット文字列

    Returns:
        ルートロガー (logging.Logger)
    """
    if log_format is None:
        log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True,  # 既存の設定を上書き
    )

    logger = logging.getLogger("world_news")
    logger.setLevel(level)
    return logger
