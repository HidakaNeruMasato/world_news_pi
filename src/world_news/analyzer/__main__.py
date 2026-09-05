"""Article Analyzer サービス起動エントリーポイント"""

import sys
from world_news.logging import setup_logging
from world_news.analyzer.worker import ArticleAnalyzerWorker


def main():
    setup_logging()
    worker = ArticleAnalyzerWorker()
    try:
        worker.start_loop()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
