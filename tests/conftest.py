"""pytest 共通フィクスチャ"""

import tempfile
from pathlib import Path
import pytest
from world_news.config import AppConfig


@pytest.fixture
def temp_config_file():
    """一時的な YAML 設定ファイルを生成するフィクスチャ"""
    content = """
system:
  timezone: "Asia/Tokyo"
  event_lifetime_hours: 12
  min_display_confidence: 0.8

pi3:
  host: "test-pi3"
  submit_url: "http://test-pi4:8080/api/v1/internal/articles"

pi4:
  host: "test-pi4"
  api_port: 8080

llm:
  provider: "llama_cpp"
  model_id: "test-model"
"""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml", encoding="utf-8") as f:
        f.write(content)
        temp_path = Path(f.name)

    yield temp_path

    if temp_path.exists():
        temp_path.unlink()
