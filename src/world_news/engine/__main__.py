"""Event Engine 常駐サービスエントリーポイント"""

import sys
import logging
from world_news.logging import setup_logging
from world_news.engine.worker import EventEngineWorker


def main():
    setup_logging()
    logger = logging.getLogger("world_news.engine.main")
    logger.info("Initializing World News Event Engine Service...")

    worker = EventEngineWorker()
    try:
        worker.run_loop()
    except Exception as e:
        logger.critical(f"Fatal error in Event Engine Service: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
