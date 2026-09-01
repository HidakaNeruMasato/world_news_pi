"""設定ローダーのユニットテスト"""

from pathlib import Path
from world_news.config import load_config, AppConfig


def test_default_config():
    """存在しないパスを指定した際、デフォルト設定が読み込まれるかテスト"""
    config = load_config("non_existent_config_file_12345.yaml")
    assert isinstance(config, AppConfig)
    assert config.system.timezone == "Asia/Tokyo"
    assert config.system.event_lifetime_hours == 6
    assert config.pi4.api_port == 8080


def test_load_custom_config(temp_config_file: Path):
    """カスタム YAML ファイルの読み込みテスト"""
    config = load_config(temp_config_file)
    assert config.system.event_lifetime_hours == 12
    assert config.system.min_display_confidence == 0.8
    assert config.pi3.host == "test-pi3"
    assert config.llm.model_id == "test-model"
