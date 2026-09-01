"""サブパッケージ構造のインポートテスト"""

import world_news
import world_news.collector
import world_news.analyzer
import world_news.api


def test_package_structure():
    """全サブパッケージが正常に参照・インポートできることを確認"""
    assert world_news.__version__ == "0.1.0"
    assert world_news.collector.__version__ == "0.1.0"
    assert world_news.analyzer.__version__ == "0.1.0"
    assert world_news.api.__version__ == "0.1.0"
