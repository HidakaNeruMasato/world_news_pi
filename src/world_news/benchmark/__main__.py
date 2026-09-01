"""T005 LLM ベンチマーク一括実行エントリーポイント"""

import os
import sys
from pathlib import Path
from world_news.logging import setup_logging
from world_news.benchmark.runner import BenchmarkRunner, ModelConfig, load_ground_truth


def main():
    setup_logging()
    
    gt_path = Path("tests/fixtures/benchmark/ground_truth.json")
    if not gt_path.exists():
        gt_path = Path(__file__).parents[3] / "tests" / "fixtures" / "benchmark" / "ground_truth.json"

    ground_truth = load_ground_truth(gt_path)

    # 評価モデル候補の設定一覧
    models = [
        ModelConfig(
            name="Qwen2.5-1.5B-Instruct-Q4_K_M",
            file_path=Path("/home/hidakamasato/models/qwen2.5-1.5b-instruct-q4_k_m.gguf"),
            quantization="Q4_K_M",
            license_type="Apache-2.0",
        ),
        ModelConfig(
            name="Llama-3.2-1B-Instruct-Q4_K_M",
            file_path=Path("/home/hidakamasato/models/Llama-3.2-1B-Instruct-Q4_K_M.gguf"),
            quantization="Q4_K_M",
            license_type="Llama 3.2 Community License",
        ),
        ModelConfig(
            name="Qwen2.5-3B-Instruct-Q3_K_M",
            file_path=Path("/home/hidakamasato/models/qwen2.5-3b-instruct-q3_k_m.gguf"),
            quantization="Q3_K_M",
            license_type="Apache-2.0",
        ),
    ]

    runner = BenchmarkRunner(output_dir=Path("benchmark/results"))

    for model_cfg in models:
        if model_cfg.file_path.exists():
            runner.evaluate_model(model_cfg, ground_truth)
        else:
            print(f"Skipping model {model_cfg.name} (file not found: {model_cfg.file_path})")


if __name__ == "__main__":
    main()
