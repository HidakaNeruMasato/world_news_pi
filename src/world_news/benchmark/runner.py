"""T005 ベンチマークランナーモジュール"""

import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

from world_news.benchmark.schemas import (
    GroundTruthItem,
    ArticleBenchmarkMetric,
    ModelBenchmarkSummary,
)
from world_news.benchmark.prompts import SYSTEM_PROMPT, build_user_prompt
from world_news.benchmark.evaluator import (
    extract_and_validate_json,
    calculate_percentiles,
    evaluate_accuracy,
)

logger = logging.getLogger("world_news.benchmark")


def get_ram_usage_mb() -> float:
    """現在のシステム/プロセスメモリ使用量 (MB) を取得します"""
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
        mem_info = {}
        for line in lines:
            parts = line.split(":")
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip().split()[0]
                mem_info[key] = int(val)
        total = mem_info.get("MemTotal", 0)
        available = mem_info.get("MemAvailable", 0)
        used_kb = total - available
        return round(used_kb / 1024.0, 2)
    except Exception:
        return 0.0


def load_ground_truth(file_path: Path) -> List[GroundTruthItem]:
    """Ground Truth 正解ラベルデータを読み込みます"""
    if not file_path.exists():
        raise FileNotFoundError(f"Ground truth file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [GroundTruthItem(**item) for item in data]


class ModelConfig:
    """ベンチマーク対象モデルの設定"""
    def __init__(
        self,
        name: str,
        file_path: Path,
        quantization: str,
        license_type: str,
        llama_cli_path: Optional[Path] = None,
        threads: int = 4,
        context_size: int = 2048,
        temperature: float = 0.1,
    ):
        self.name = name
        self.file_path = file_path
        self.quantization = quantization
        self.license_type = license_type
        self.llama_cli_path = llama_cli_path or Path("/home/hidakamasato/llama.cpp/build/bin/llama-cli")
        self.threads = threads
        self.context_size = context_size
        self.temperature = temperature


class BenchmarkRunner:
    """ローカル LLM ベンチマーク実行クラス"""

    def __init__(self, output_dir: Path = Path("benchmark/results")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_inference_cli(
        self, model_cfg: ModelConfig, prompt: str
    ) -> Tuple[str, float, Optional[float]]:
        """llama-cli を使用して単一プロンプト推論を実行します

        Returns:
            Tuple[output_text, latency_ms, tokens_per_sec]
        """
        if not model_cfg.llama_cli_path.exists():
            raise FileNotFoundError(f"llama-cli executable not found at {model_cfg.llama_cli_path}")
        if not model_cfg.file_path.exists():
            raise FileNotFoundError(f"Model file not found at {model_cfg.file_path}")

        cmd = [
            str(model_cfg.llama_cli_path),
            "-m", str(model_cfg.file_path),
            "-p", f"{SYSTEM_PROMPT}\n\n{prompt}",
            "-n", "256",
            "-t", str(model_cfg.threads),
            "-c", str(model_cfg.context_size),
            "--temp", str(model_cfg.temperature),
            "--no-display-prompt",
        ]

        start_time = time.perf_counter()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            output_text = result.stdout.strip()
            return output_text, round(latency_ms, 2), None
        except subprocess.TimeoutExpired:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return "ERROR: Inference Timeout", round(latency_ms, 2), None

    def evaluate_model(
        self, model_cfg: ModelConfig, ground_truth: List[GroundTruthItem]
    ) -> ModelBenchmarkSummary:
        """指定モデルについて全 Ground Truth データのベンチマークを実行し集計結果を返します"""
        logger.info(f"=== Starting Benchmark for Model: {model_cfg.name} ===")

        ram_idle = get_ram_usage_mb()
        load_start = time.perf_counter()
        model_size_mb = round(model_cfg.file_path.stat().st_size / (1024.0 * 1024.0), 2) if model_cfg.file_path.exists() else 0.0
        load_time_ms = round((time.perf_counter() - load_start) * 1000.0, 2)

        peak_ram = ram_idle
        metrics: List[ArticleBenchmarkMetric] = []
        latencies: List[float] = []

        valid_json_count = 0
        schema_valid_count = 0
        is_event_correct_count = 0
        country_correct_count = 0
        location_correct_count = 0
        oom_flag = False

        for item in ground_truth:
            prompt = build_user_prompt(item.title, item.description or "", item.source_country)

            ram_before = get_ram_usage_mb()
            peak_ram = max(peak_ram, ram_before)

            try:
                output_text, latency_ms, tps = self.run_inference_cli(model_cfg, prompt)
            except Exception as e:
                logger.error(f"Inference error on article {item.id}: {e}")
                output_text = f"ERROR: {str(e)}"
                latency_ms = 0.0
                tps = None
                if "out of memory" in str(e).lower() or "oom" in str(e).lower():
                    oom_flag = True

            ram_after = get_ram_usage_mb()
            peak_ram = max(peak_ram, ram_after)

            valid_json, schema_valid, enum_valid, parsed_obj, parsed_dict = extract_and_validate_json(output_text)
            is_event_ok, country_ok, loc_ok = evaluate_accuracy(parsed_obj, item)

            if valid_json:
                valid_json_count += 1
            if schema_valid:
                schema_valid_count += 1
            if is_event_ok:
                is_event_correct_count += 1
            if country_ok:
                country_correct_count += 1
            if loc_ok:
                location_correct_count += 1

            latencies.append(latency_ms)

            metrics.append(
                ArticleBenchmarkMetric(
                    article_id=item.id,
                    latency_ms=latency_ms,
                    tokens_per_sec=tps,
                    raw_output=output_text,
                    parsed_json=parsed_dict,
                    valid_json=valid_json,
                    schema_valid=schema_valid,
                    enum_valid=enum_valid,
                    is_event_correct=is_event_ok,
                    country_correct=country_ok,
                    location_correct=loc_ok,
                    ram_usage_mb=ram_after,
                )
            )

        ram_post = get_ram_usage_mb()
        percentiles = calculate_percentiles(latencies)
        n = len(ground_truth)

        summary = ModelBenchmarkSummary(
            model_name=model_cfg.name,
            file_name=model_cfg.file_path.name,
            quantization=model_cfg.quantization,
            model_size_mb=model_size_mb,
            license_type=model_cfg.license_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            threads=model_cfg.threads,
            context_size=model_cfg.context_size,
            temperature=model_cfg.temperature,
            total_articles=n,
            load_time_ms=load_time_ms,
            ram_idle_mb=ram_idle,
            ram_peak_mb=peak_ram,
            ram_post_mb=ram_post,
            latencies_ms=latencies,
            min_latency_ms=percentiles["min"],
            median_latency_ms=percentiles["median"],
            p95_latency_ms=percentiles["p95"],
            max_latency_ms=percentiles["max"],
            avg_tokens_per_sec=0.0,
            valid_json_rate=round(valid_json_count / n * 100.0, 2) if n > 0 else 0.0,
            schema_valid_rate=round(schema_valid_count / n * 100.0, 2) if n > 0 else 0.0,
            is_event_accuracy=round(is_event_correct_count / n * 100.0, 2) if n > 0 else 0.0,
            country_accuracy=round(country_correct_count / n * 100.0, 2) if n > 0 else 0.0,
            location_accuracy=round(location_correct_count / n * 100.0, 2) if n > 0 else 0.0,
            oom_occurred=oom_flag,
            details=metrics,
        )

        out_file = self.output_dir / f"{model_cfg.name.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(summary.model_dump_json(indent=2))

        logger.info(f"Saved benchmark summary for {model_cfg.name} to {out_file}")
        return summary
