"""ベンチマーク精度判定および評価集計モジュール"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from world_news.benchmark.schemas import (
    LLMEventOutput,
    GroundTruthItem,
    ArticleBenchmarkMetric,
    EventTypeEnum,
)


def extract_json_string(text: str) -> str:
    """LLM 出力から Markdown フェンス等を剥がして純粋な JSON 文字列を取り出します"""
    cleaned = text.strip()
    # ```json ... ``` または ``` ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if match:
        return match.group(1)

    # 最初の { から 最後の } まで
    match_braces = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if match_braces:
        return match_braces.group(1)

    return cleaned


def extract_and_validate_json(raw_text: str) -> Tuple[bool, bool, bool, Optional[LLMEventOutput], Optional[dict]]:
    """JSON パース、Schema バリデーション、Enum バリデーションを実行します

    Returns:
        Tuple[valid_json, schema_valid, enum_valid, parsed_model, parsed_dict]
    """
    json_str = extract_json_string(raw_text)
    try:
        data = json.loads(json_str)
    except Exception:
        return False, False, False, None, None

    if not isinstance(data, dict):
        return True, False, False, None, data

    valid_json = True
    enum_valid = False
    schema_valid = False
    model_obj = None

    # Enum チェック
    event_type = data.get("event_type")
    valid_enums = [e.value for e in EventTypeEnum]
    if event_type in valid_enums:
        enum_valid = True

    try:
        model_obj = LLMEventOutput(**data)
        schema_valid = True
    except Exception:
        schema_valid = False

    return valid_json, schema_valid, enum_valid, model_obj, data


def calculate_percentiles(numbers: List[float]) -> Dict[str, float]:
    """Min, Median (P50), P95, Max のパーセンタイル値を算出します"""
    if not numbers:
        return {"min": 0.0, "median": 0.0, "p95": 0.0, "max": 0.0}

    sorted_nums = sorted(numbers)
    n = len(sorted_nums)

    min_val = sorted_nums[0]
    max_val = sorted_nums[-1]

    # Median (P50)
    if n % 2 == 1:
        median_val = sorted_nums[n // 2]
    else:
        median_val = (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2.0

    # P95
    p95_idx = int(round(0.95 * (n - 1)))
    p95_val = sorted_nums[min(p95_idx, n - 1)]

    return {
        "min": round(min_val, 2),
        "median": round(median_val, 2),
        "p95": round(p95_val, 2),
        "max": round(max_val, 2),
    }


def evaluate_accuracy(
    output: Optional[LLMEventOutput], gt: GroundTruthItem
) -> Tuple[bool, bool, bool]:
    """LLM 出力と Ground Truth 正解ラベルを対比して正解精度を判定します

    Returns:
        Tuple[is_event_correct, country_correct, location_correct]
    """
    if output is None:
        return False, False, False

    # 1. is_event 一致
    is_event_correct = (output.is_event == gt.expected_is_event)

    # 2. event_country 一致
    gt_country = gt.expected_event_country.upper() if gt.expected_event_country else None
    out_country = output.event_country.upper() if output.event_country else None
    country_correct = (out_country == gt_country)

    # 3. location (city/region) 一致判定
    location_correct = True
    if gt.expected_event_city:
        out_city = (output.event_city or "").lower()
        if gt.expected_event_city.lower() not in out_city:
            location_correct = False
    elif gt.expected_event_region:
        out_region = (output.event_region or "").lower()
        if gt.expected_event_region.lower() not in out_region:
            location_correct = False
    else:
        # 正解で地点がなしの場合、モデルも地名を勝手に作っていないか
        if output.event_city or output.event_region:
            location_correct = False

    return is_event_correct, country_correct, location_correct
