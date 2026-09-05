"""Qwen2.5-1.5B LLM 推論実行クライアント"""

import os
import sys
import json
import time
import subprocess
import re
import urllib.request
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

from world_news.schemas import AnalysisErrorCode
from world_news.analyzer.schemas import LLMAnalysisOutput
from world_news.benchmark.evaluator import extract_json_string
from world_news.analyzer.prompts import SYSTEM_PROMPT_V1, build_analysis_prompt, PROMPT_VERSION

logger = logging.getLogger("world_news.analyzer.llm")


class LLMInferenceResult:
    def __init__(
        self,
        raw_output: str,
        parsed_output: Optional[LLMAnalysisOutput] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        inference_time_ms: float = 0.0,
    ):
        self.raw_output = raw_output
        self.parsed_output = parsed_output
        self.error_code = error_code
        self.error_message = error_message
        self.inference_time_ms = inference_time_ms


class Qwen25LLMClient:
    """Qwen2.5-1.5B-Instruct GGUF 推論クライアント (HTTP API 優先 + CLI フォールバック)"""

    def __init__(
        self,
        model_path: Optional[Path] = None,
        llama_cli_path: Optional[Path] = None,
        server_url: str = "http://127.0.0.1:8088",
        threads: int = 4,
        context_size: int = 2048,
        temperature: float = 0.1,
        timeout_seconds: int = 180,
    ):
        self.model_name = "Qwen2.5-1.5B-Instruct-GGUF"
        self.model_version = "Q4_K_M"
        self.prompt_version = PROMPT_VERSION
        self.model_path = model_path or Path("/home/hidakamasato/models/qwen2.5-1.5b-instruct-q4_k_m.gguf")
        self.llama_cli_path = llama_cli_path or Path("/home/hidakamasato/llama.cpp/build/bin/llama-cli")
        self.server_url = server_url.rstrip("/")
        self.threads = threads
        self.context_size = context_size
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds

    def _infer_via_http(self, full_prompt: str) -> Optional[Tuple[str, float]]:
        """常駐している llama-server (HTTP API) 経由で推論を試みます"""
        import urllib.request
        import urllib.error

        url = f"{self.server_url}/completion"
        payload = {
            "prompt": full_prompt,
            "n_predict": 256,
            "temperature": self.temperature,
            "stop": ["}\n\n", "}\n}", "```"],
            "stream": False,
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data_bytes, headers={"Content-Type": "application/json"}, method="POST"
        )

        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                if resp.status == 200:
                    res_body = resp.read().decode("utf-8")
                    res_json = json.loads(res_body)
                    raw_text = res_json.get("content", "").strip()
                    inf_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)
                    return raw_text, inf_time_ms
        except Exception as e:
            logger.debug(f"llama-server HTTP API not available ({e}), falling back to llama-cli")

        return None

    def analyze_article(self, title: str, description: str = "", source_country: str = "XX") -> LLMInferenceResult:
        """単一ニュース記事のプロンプト構築と LLM 推論を実行します"""

        user_prompt = build_analysis_prompt(title, description, source_country)
        full_prompt = f"{SYSTEM_PROMPT_V1}\n\n{user_prompt}"

        # 1. まず常駐 llama-server (HTTP) 経由を試行 (高速: 1~2秒)
        http_res = self._infer_via_http(full_prompt)
        if http_res is not None:
            raw_text, inf_time_ms = http_res
            return self._parse_and_validate(raw_text, inf_time_ms)

        # 2. HTTP 未起動の場合は llama-cli ワンショット実行にフォールバック (モデルロード含め約50秒)
        if not self.model_path.exists():
            msg = f"Model file not found: {self.model_path}"
            logger.error(msg)
            return LLMInferenceResult(
                raw_output="",
                error_code=AnalysisErrorCode.MODEL_UNAVAILABLE.value,
                error_message=msg,
            )

        if not self.llama_cli_path.exists():
            msg = f"llama-cli binary not found: {self.llama_cli_path}"
            logger.error(msg)
            return LLMInferenceResult(
                raw_output="",
                error_code=AnalysisErrorCode.MODEL_UNAVAILABLE.value,
                error_message=msg,
            )

        cmd = [
            str(self.llama_cli_path),
            "-m", str(self.model_path),
            "-p", full_prompt,
            "-n", "256",
            "-t", str(self.threads),
            "-c", str(self.context_size),
            "--temp", str(self.temperature),
            "--no-display-prompt",
        ]

        t0 = time.perf_counter()
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout_seconds)
            inf_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)
            raw_text = res.stdout.strip()
        except subprocess.TimeoutExpired:
            inf_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)
            msg = f"LLM inference timed out after {self.timeout_seconds}s"
            logger.warning(msg)
            return LLMInferenceResult(
                raw_output="ERROR: Timeout",
                error_code=AnalysisErrorCode.TIMEOUT.value,
                error_message=msg,
                inference_time_ms=inf_time_ms,
            )
        except Exception as e:
            inf_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)
            msg = f"Unexpected runtime error in LLM process: {str(e)}"
            logger.error(msg)
            return LLMInferenceResult(
                raw_output=f"ERROR: {str(e)}",
                error_code=AnalysisErrorCode.UNEXPECTED_RUNTIME_ERROR.value,
                error_message=msg,
                inference_time_ms=inf_time_ms,
            )

        return self._parse_and_validate(raw_text, inf_time_ms)

    def _parse_and_validate(self, raw_text: str, inf_time_ms: float) -> LLMInferenceResult:
        """レスポンス文字列からの JSON 抽出と Pydantic スキーマ検証を行います"""
        if not raw_text:
            return LLMInferenceResult(
                raw_output="",
                error_code=AnalysisErrorCode.MALFORMED_OUTPUT.value,
                error_message="Raw output is empty",
                inference_time_ms=inf_time_ms,
            )

        json_str = extract_json_string(raw_text)
        
        # 最初の { から 最後の } までの抽出をフォールバックとして試行
        if not json_str or not json_str.startswith("{"):
            first_b = raw_text.find("{")
            last_b = raw_text.rfind("}")
            if first_b != -1 and last_b != -1 and last_b > first_b:
                json_str = raw_text[first_b:last_b + 1].strip()

        data = None
        parse_err_msg = ""
        
        # 段階的 JSON パース試行
        try:
            data = json.loads(json_str)
        except Exception as e1:
            parse_err_msg = str(e1)
            # Extra data エラー対策: json.JSONDecoder().raw_decode() を使用して最初の有効オブジェクトをデコード
            try:
                decoder = json.JSONDecoder()
                clean_target = json_str.lstrip()
                data, idx = decoder.raw_decode(clean_target)
            except Exception as e2:
                # { ... } の最初のブロックのみを正規表現で抽出
                brace_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", json_str, re.DOTALL)
                if brace_match:
                    try:
                        data = json.loads(brace_match.group(0))
                    except Exception as e3:
                        parse_err_msg = f"{str(e1)} | raw_decode: {str(e2)} | regex: {str(e3)}"

        if data is None or not isinstance(data, dict):
            return LLMInferenceResult(
                raw_output=raw_text,
                error_code=AnalysisErrorCode.JSON_PARSE_FAILURE.value,
                error_message=f"JSON parse error: {parse_err_msg}",
                inference_time_ms=inf_time_ms,
            )

        try:
            model_obj = LLMAnalysisOutput(**data)
            return LLMInferenceResult(
                raw_output=raw_text,
                parsed_output=model_obj,
                inference_time_ms=inf_time_ms,
            )
        except Exception as e:
            return LLMInferenceResult(
                raw_output=raw_text,
                error_code=AnalysisErrorCode.SCHEMA_VALIDATION_FAILURE.value,
                error_message=f"Schema validation error: {str(e)}",
                inference_time_ms=inf_time_ms,
            )

