"""Pi4 REST API アプリケーションエントリーポイント"""

import uvicorn
from world_news.config import load_config
from world_news.logging import setup_logging

def main():
    setup_logging()
    config = load_config()
    uvicorn.run(
        "world_news.api.app:app",
        host="0.0.0.0",
        port=config.pi4.api_port,
        reload=False,
    )

if __name__ == "__main__":
    main()
