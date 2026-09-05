"""T006 Pi4 Article Analyzer ユニットテスト (全23項目)"""

import json
import sqlite3
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from world_news.schemas import EventCategory, AnalysisErrorCode, JobStatus
from world_news.api.database import Pi4Database
from world_news.analyzer.schemas import (
    LLMAnalysisOutput,
    ISO_COUNTRY_CODES,
    detect_location_hallucination,
)
from world_news.analyzer.prompts import (
    PROMPT_VERSION,
    SYSTEM_PROMPT_V1,
    build_analysis_prompt,
)
from world_news.analyzer.llm_client import (
    Qwen25LLMClient,
    LLMInferenceResult,
)
from world_news.analyzer.worker import ArticleAnalyzerWorker


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_analyzer.db"
    db = Pi4Database(db_path=db_file)
    return db


@pytest.fixture
def sample_article_payload():
    return {
        "source_id": 1,
        "source_country": "GB",
        "external_id": "bbc_12345",
        "title": "Strong Earthquake Hits Wajima City in Japan",
        "description": "A magnitude 6.8 earthquake rocked Ishikawa, Japan.",
        "url": "https://bbc.com/news/12345",
        "published_at": "2026-09-01T12:00:00Z",
    }


# 1. LLM input generation
def test_llm_input_generation():
    prompt = build_analysis_prompt("Earthquake in Tokyo", "Mag 5 earthquake", "GB")
    assert "Earthquake in Tokyo" in prompt
    assert "GB" in prompt
    assert "reference ONLY" in prompt


# 2. prompt versioning
def test_prompt_versioning():
    assert PROMPT_VERSION == "analysis_prompt_v1"
    assert "DO NOT copy" in SYSTEM_PROMPT_V1


# 3. valid JSON parsing
def test_valid_json_parsing():
    raw_json = '{"is_event": true, "event_type": "earthquake", "event_country": "JP", "confidence": 0.95}'
    model_obj = LLMAnalysisOutput(**json.loads(raw_json))
    assert model_obj.is_event is True
    assert model_obj.event_country == "JP"


# 4. malformed JSON
def test_malformed_json(tmp_path):
    dummy_model = tmp_path / "model.gguf"
    dummy_cli = tmp_path / "llama-cli"
    dummy_model.write_text("dummy")
    dummy_cli.write_text("dummy")

    client = Qwen25LLMClient(model_path=dummy_model, llama_cli_path=dummy_cli)
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="BROKEN NOT JSON {{{")
        res = client.analyze_article("Title", "Desc", "JP")

    assert res.error_code == AnalysisErrorCode.JSON_PARSE_FAILURE.value
    assert res.raw_output == "BROKEN NOT JSON {{{"


# 5. schema validation
def test_schema_validation():
    data = {
        "is_event": True,
        "event_type": "earthquake",
        "event_country": "jp",
        "event_city": "Wajima",
        "confidence": 0.9,
    }
    out = LLMAnalysisOutput(**data)
    assert out.event_country == "JP"  # 大文字変換


# 6. invalid event_type
def test_invalid_event_type():
    data = {
        "is_event": True,
        "event_type": "quake",  # マッピングロジックで earthquake へ修正されること
        "event_country": "JP",
    }
    out = LLMAnalysisOutput(**data)
    assert out.event_type == "earthquake"


# 7. invalid country code
def test_invalid_country_code():
    data = {
        "is_event": True,
        "event_type": "earthquake",
        "event_country": "INVALID_CODE",
    }
    with pytest.raises(ValueError):
        LLMAnalysisOutput(**data)


# 8. null location
def test_null_location():
    data = {
        "is_event": True,
        "event_type": "politics",
        "event_country": None,
        "event_region": None,
        "event_city": None,
        "location_name": None,
    }
    out = LLMAnalysisOutput(**data)
    assert out.event_country is None
    assert out.event_city is None


# 9. is_event=false
def test_is_event_false():
    data = {
        "is_event": False,
        "event_type": "economy",
        "event_country": None,
    }
    out = LLMAnalysisOutput(**data)
    assert out.is_event is False


# 10. event generation
def test_event_generation(test_db, sample_article_payload):
    article_id, _ = test_db.insert_article_with_job(sample_article_payload)
    job = test_db.claim_next_job()

    analysis_data = {
        "model_name": "Qwen2.5-1.5B-Instruct-GGUF",
        "model_version": "Q4_K_M",
        "prompt_version": "analysis_prompt_v1",
        "raw_output": '{"is_event": true}',
        "parsed_output": {"is_event": True, "event_type": "earthquake", "event_country": "JP"},
        "is_event": True,
        "event_type": "earthquake",
        "event_country": "JP",
        "event_city": "Wajima",
        "confidence": 0.95,
        "inference_time_ms": 1200.0,
    }

    analysis_id, event_id = test_db.save_analysis_result(article_id, job["job_id"], analysis_data)

    assert analysis_id is not None
    assert event_id is not None

    stats = test_db.get_stats()
    assert stats["active_events"] == 1
    assert stats["unresolved_events"] == 1


# 11. non-event does not create Event
def test_non_event_does_not_create_event(test_db, sample_article_payload):
    article_id, _ = test_db.insert_article_with_job(sample_article_payload)
    job = test_db.claim_next_job()

    analysis_data = {
        "model_name": "Qwen2.5-1.5B-Instruct-GGUF",
        "raw_output": '{"is_event": false}',
        "is_event": False,
        "event_type": "economy",
    }

    analysis_id, event_id = test_db.save_analysis_result(article_id, job["job_id"], analysis_data)

    assert analysis_id is not None
    assert event_id is None
    assert test_db.get_stats()["active_events"] == 0


# 12. job pending -> processing -> completed
def test_job_pending_processing_completed(test_db, sample_article_payload):
    article_id, _ = test_db.insert_article_with_job(sample_article_payload)
    assert test_db.get_stats()["pending_jobs"] == 1

    job = test_db.claim_next_job()
    assert job is not None
    assert test_db.get_stats()["processing_jobs"] == 1

    test_db.save_analysis_result(article_id, job["job_id"], {"is_event": False})
    assert test_db.get_stats()["completed_jobs"] == 1


# 13. job failure
def test_job_failure(test_db, sample_article_payload):
    article_id, _ = test_db.insert_article_with_job(sample_article_payload)
    job = test_db.claim_next_job()

    test_db.fail_job(
        job_id=job["job_id"],
        article_id=article_id,
        error_code=AnalysisErrorCode.MODEL_UNAVAILABLE.value,
        error_message="Model file missing",
        max_retries=0,  # 直ちに失敗
    )

    assert test_db.get_stats()["failed_jobs"] == 1


# 14. retry
def test_retry(test_db, sample_article_payload):
    article_id, _ = test_db.insert_article_with_job(sample_article_payload)
    job = test_db.claim_next_job()

    test_db.fail_job(
        job_id=job["job_id"],
        article_id=article_id,
        error_code=AnalysisErrorCode.TIMEOUT.value,
        error_message="Timeout error",
        max_retries=3,  # リトライ可能
    )

    # 状態が pending へ引き戻されていること
    assert test_db.get_stats()["pending_jobs"] == 1


# 15. stale processing recovery
def test_stale_processing_recovery(test_db, sample_article_payload):
    article_id, _ = test_db.insert_article_with_job(sample_article_payload)
    job = test_db.claim_next_job()

    # DB 内の started_at を過去15分前へ直接変更
    with test_db._get_connection() as conn:
        conn.execute("UPDATE processing_jobs SET started_at = '2026-01-01T00:00:00Z' WHERE id = ?", (job["job_id"],))
        conn.commit()

    recovered = test_db.recover_stale_jobs(timeout_minutes=10)
    assert recovered == 1
    assert test_db.get_stats()["pending_jobs"] == 1


# 16. Test LLMAnalysisOutput with None event_type and Extra data JSON recovery
def test_schema_optional_event_type():
    data = {
        "is_event": False,
        "event_type": None,
        "event_country": None,
        "confidence": 0.0,
    }
    output = LLMAnalysisOutput(**data)
    assert output.is_event is False
    assert output.event_type == "other"


def test_llm_client_extra_data_recovery(monkeypatch, tmp_path):
    client = Qwen25LLMClient(model_path=tmp_path / "dummy.gguf")

    raw_with_extra = '{"is_event": true, "event_type": "accident", "confidence": 0.9} Extra commentary after JSON'
    res = client._parse_and_validate(raw_with_extra, inf_time_ms=10.0)

    assert res.error_code is None
    assert res.parsed_output is not None
    assert res.parsed_output.is_event is True
    assert res.parsed_output.event_type == "accident"



# 16. model unavailable
def test_model_unavailable(tmp_path):
    client = Qwen25LLMClient(
        model_path=tmp_path / "non_existent.gguf",
        llama_cli_path=tmp_path / "non_existent_cli",
    )
    res = client.analyze_article("Title", "Desc", "JP")
    assert res.error_code == AnalysisErrorCode.MODEL_UNAVAILABLE.value


# 17. LLM timeout
def test_llm_timeout(tmp_path):
    dummy_model = tmp_path / "model.gguf"
    dummy_cli = tmp_path / "llama-cli"
    dummy_model.write_text("dummy")
    dummy_cli.write_text("dummy")

    client = Qwen25LLMClient(model_path=dummy_model, llama_cli_path=dummy_cli, timeout_seconds=1)
    with patch("subprocess.run", side_effect=pytest.importorskip("subprocess").TimeoutExpired(cmd="test", timeout=1)):
        res = client.analyze_article("Title", "Desc", "JP")

    assert res.error_code == AnalysisErrorCode.TIMEOUT.value


# 18. inference error
def test_inference_error(tmp_path):
    dummy_model = tmp_path / "model.gguf"
    dummy_cli = tmp_path / "llama-cli"
    dummy_model.write_text("dummy")
    dummy_cli.write_text("dummy")

    client = Qwen25LLMClient(model_path=dummy_model, llama_cli_path=dummy_cli)
    with patch("subprocess.run", side_effect=RuntimeError("Process crash")):
        res = client.analyze_article("Title", "Desc", "JP")

    assert res.error_code == AnalysisErrorCode.UNEXPECTED_RUNTIME_ERROR.value


# 19. source_country != event_country
def test_source_country_not_equal_event_country():
    # BBC (source_country: GB) が日本の地震を報道
    prompt = build_analysis_prompt("Earthquake in Japan", "Mag 6.8", "GB")
    assert "GB" in prompt
    assert "reference ONLY - do not copy" in prompt


# 20. historical event handling
def test_historical_event_handling():
    # 30年前の歴史振り返り
    raw_output = '{"is_event": false, "event_type": "earthquake", "event_country": "JP"}'
    out = LLMAnalysisOutput(**json.loads(raw_output))
    assert out.is_event is False


# 21. multiple-country article
def test_multiple_country_article():
    raw_output = '{"is_event": true, "event_type": "politics", "event_country": "FR", "event_city": "Paris"}'
    out = LLMAnalysisOutput(**json.loads(raw_output))
    assert out.event_country == "FR"
    assert out.event_city == "Paris"


# 22. raw_output storage
def test_raw_output_storage(test_db, sample_article_payload):
    article_id, _ = test_db.insert_article_with_job(sample_article_payload)
    job = test_db.claim_next_job()

    raw_text = '{"is_event": true, "event_type": "accident"}'
    test_db.save_analysis_result(article_id, job["job_id"], {"raw_output": raw_text, "is_event": True, "event_type": "accident"})

    with test_db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT raw_output FROM analyses WHERE article_id = ?", (article_id,))
        row = cursor.fetchone()
        assert row["raw_output"] == raw_text


# 23. analysis metadata storage
def test_analysis_metadata_storage(test_db, sample_article_payload):
    article_id, _ = test_db.insert_article_with_job(sample_article_payload)
    job = test_db.claim_next_job()

    analysis_data = {
        "model_name": "Qwen2.5-1.5B-Instruct-GGUF",
        "model_version": "Q4_K_M",
        "prompt_version": "analysis_prompt_v1",
        "inference_time_ms": 1450.5,
        "is_event": False,
    }
    test_db.save_analysis_result(article_id, job["job_id"], analysis_data)

    with test_db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT model_name, prompt_version, inference_time_ms FROM analyses WHERE article_id = ?", (article_id,))
        row = cursor.fetchone()
        assert row["model_name"] == "Qwen2.5-1.5B-Instruct-GGUF"
        assert row["prompt_version"] == "analysis_prompt_v1"
        assert row["inference_time_ms"] == 1450.5
