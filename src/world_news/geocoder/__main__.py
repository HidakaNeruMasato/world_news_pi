"""Event Geocoder 常駐サービスエントリーポイント"""

import sys
import logging
from world_news.logging import setup_logging
from world_news.geocoder.worker import EventGeocoderWorker


def main():
    setup_logging()
    logger = logging.getLogger("world_news.geocoder.main")
    logger.info("Initializing World News Event Geocoder Service...")

    worker = EventGeocoderWorker()
    try:
        worker.run_loop()
    except Exception as e:
        logger.critical(f"Fatal error in Geocoder Service: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
