"""T005 LLM ベンチマークユニットテスト (全10項目)"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from world_news.benchmark.schemas import (
    LLMEventOutput,
    GroundTruthItem,
    ModelBenchmarkSummary,
    EventTypeEnum,
)
from world_news.benchmark.prompts import SYSTEM_PROMPT, build_user_prompt
from world_news.benchmark.evaluator import (
    extract_json_string,
    extract_and_validate_json,
    calculate_percentiles,
    evaluate_accuracy,
)
from world_news.benchmark.runner import (
    BenchmarkRunner,
    ModelConfig,
    load_ground_truth,
)


@pytest.fixture
def sample_gt_path(tmp_path):
    gt_file = tmp_path / "ground_truth.json"
    data = [
        {
            "id": 1,
            "source_id": 1,
            "source_country": "JP",
            "title": "Earthquake in Wajima",
            "description": "Mag 6.8 earthquake in Wajima city, Ishikawa",
            "expected_is_event": True,
            "expected_event_type": "earthquake",
            "expected_event_country": "JP",
            "expected_event_region": "Ishikawa",
            "expected_event_city": "Wajima",
            "case_category": "Case A",
        }
    ]
    gt_file.write_text(json.dumps(data), encoding="utf-8")
    return gt_file


# 1. benchmark input loading
def test_benchmark_input_loading(sample_gt_path):
    items = load_ground_truth(sample_gt_path)
    assert len(items) == 1
    assert items[0].title == "Earthquake in Wajima"
    assert items[0].expected_event_country == "JP"


# 2. model configuration loading
def test_model_configuration_loading(tmp_path):
    dummy_model = tmp_path / "model.gguf"
    dummy_model.write_text("dummy")

    cfg = ModelConfig(
        name="TestModel",
        file_path=dummy_model,
        quantization="Q4_K_M",
        license_type="Apache-2.0",
        threads=4,
    )
    assert cfg.name == "TestModel"
    assert cfg.quantization == "Q4_K_M"
    assert cfg.threads == 4


# 3. prompt generation
def test_prompt_generation():
    prompt = build_user_prompt(
        title="Train Accident in Berlin",
        description="Two trains collided",
        source_country="GB",
    )
    assert "Train Accident in Berlin" in prompt
    assert "GB" in prompt
    assert "Publisher Country Code" in prompt


# 4. JSON extraction
def test_json_extraction():
    raw_markdown = """Here is the extracted json:
```json
{
  "is_event": true,
  "event_type": "earthquake",
  "event_country": "JP"
}
```
Thank you!"""
    cleaned = extract_json_string(raw_markdown)
    assert cleaned.startswith("{")
    assert cleaned.endswith("}")
    assert '"is_event": true' in cleaned


# 5. schema validation
def test_schema_validation():
    valid_raw = '{"is_event": true, "event_type": "earthquake", "event_country": "jp", "confidence": 0.95}'
    valid_json, schema_valid, enum_valid, model_obj, parsed_dict = extract_and_validate_json(valid_raw)

    assert valid_json is True
    assert schema_valid is True
    assert enum_valid is True
    assert model_obj.is_event is True
    assert model_obj.event_country == "JP"  # 大文字へ変換されること

    invalid_enum_raw = '{"is_event": true, "event_type": "unknown_type_enum"}'
    _, schema_v, enum_v, _, _ = extract_and_validate_json(invalid_enum_raw)
    assert enum_v is False


# 6. benchmark result storage
def test_benchmark_result_storage(tmp_path, sample_gt_path):
    items = load_ground_truth(sample_gt_path)
    dummy_model = tmp_path / "model.gguf"
    dummy_model.write_text("dummy")
    dummy_cli = tmp_path / "llama-cli"
    dummy_cli.write_text("dummy")

    cfg = ModelConfig(
        name="TestStorageModel",
        file_path=dummy_model,
        quantization="Q4_K_M",
        license_type="MIT",
        llama_cli_path=dummy_cli,
    )

    runner = BenchmarkRunner(output_dir=tmp_path)

    # CLI 呼び出しを Mock
    with patch.object(
        runner,
        "run_inference_cli",
        return_value=('{"is_event": true, "event_type": "earthquake", "event_country": "JP", "event_city": "Wajima"}', 1500.0, 10.5),
    ):
        summary = runner.evaluate_model(cfg, items)

    assert summary.total_articles == 1
    assert summary.valid_json_rate == 100.0
    assert summary.is_event_accuracy == 100.0

    # ディレクトリ内に JSON が生成されていること
    results_files = list(tmp_path.glob("*.json"))
    assert len(results_files) >= 1


# 7. latency calculation
def test_latency_calculation():
    latencies = [100.0, 200.0, 300.0]
    res = calculate_percentiles(latencies)
    assert res["min"] == 100.0
    assert res["median"] == 200.0
    assert res["max"] == 300.0


# 8. p50/p95 percentile calculation
def test_p50_p95_percentile_calculation():
    # 10 個の異なるレイテンシデータ
    latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    res = calculate_percentiles(latencies)

    assert res["min"] == 10.0
    assert res["median"] == 55.0  # 50 と 60 の平均
    assert res["p95"] == 100.0    # 95% パーセンタイル


# 9. failed inference handling
def test_failed_inference_handling(tmp_path, sample_gt_path):
    items = load_ground_truth(sample_gt_path)
    dummy_model = tmp_path / "model.gguf"
    dummy_model.write_text("dummy")

    cfg = ModelConfig(
        name="FailModel",
        file_path=dummy_model,
        quantization="Q4_K_M",
        license_type="MIT",
    )

    runner = BenchmarkRunner(output_dir=tmp_path)
    with patch.object(runner, "run_inference_cli", side_effect=RuntimeError("CLI Crash")):
        summary = runner.evaluate_model(cfg, items)

    assert summary.valid_json_rate == 0.0
    assert summary.schema_valid_rate == 0.0
    assert summary.details[0].raw_output.startswith("ERROR:")


# 10. OOM / error handling
def test_oom_error_handling(tmp_path, sample_gt_path):
    items = load_ground_truth(sample_gt_path)
    dummy_model = tmp_path / "model.gguf"
    dummy_model.write_text("dummy")

    cfg = ModelConfig(
        name="OOMModel",
        file_path=dummy_model,
        quantization="Q8_0",
        license_type="MIT",
    )

    runner = BenchmarkRunner(output_dir=tmp_path)
    with patch.object(runner, "run_inference_cli", side_effect=MemoryError("out of memory allocated")):
        summary = runner.evaluate_model(cfg, items)

    assert summary.oom_occurred is True
