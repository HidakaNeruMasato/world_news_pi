"""Article Analyzer 定期監視ワーカーモジュール"""

import time
import logging
from typing import Optional

from world_news.config import AppConfig, load_config
from world_news.api.database import Pi4Database
from world_news.analyzer.llm_client import Qwen25LLMClient, LLMInferenceResult

logger = logging.getLogger("world_news.analyzer.worker")


class ArticleAnalyzerWorker:
    """Pi4 記事解析処理バッチワーカー"""

    def __init__(
        self,
        config: Optional[AppConfig] = None,
        db: Optional[Pi4Database] = None,
        llm_client: Optional[Qwen25LLMClient] = None,
        poll_interval_seconds: int = 5,
        stale_timeout_minutes: int = 10,
    ):
        self.config = config or load_config()
        self.db = db or Pi4Database(db_path=self.config.pi4.db_path)
        self.llm_client = llm_client or Qwen25LLMClient()
        self.poll_interval_seconds = poll_interval_seconds
        self.stale_timeout_minutes = stale_timeout_minutes
        self.running = False

    def process_next_job(self) -> bool:
        """未処理ジョブを1件アトミックに取得して解析・永続化を行います。
        ジョブが処理された場合は True、処理対象がなかった場合は False を返します。
        """
        job = self.db.claim_next_job()
        if not job:
            return False

        job_id = job["job_id"]
        article_id = job["article_id"]
        title = job["title"]
        description = job["description"] or ""
        source_country = job["source_country"] or "XX"

        logger.info(f"Processing Job #{job_id} (Article #{article_id}): '{title[:40]}...'")

        # LLM 推論実行
        res: LLMInferenceResult = self.llm_client.analyze_article(
            title=title,
            description=description,
            source_country=source_country,
        )

        if res.error_code:
            logger.warning(f"Job #{job_id} failed with error code '{res.error_code}': {res.error_message}")
            self.db.fail_job(
                job_id=job_id,
                article_id=article_id,
                error_code=res.error_code,
                error_message=res.error_message or "",
            )
            # 生データも残すため analyses に失敗レコードを記録
            analysis_dict = {
                "model_name": self.llm_client.model_name,
                "model_version": self.llm_client.model_version,
                "prompt_version": self.llm_client.prompt_version,
                "raw_output": res.raw_output,
                "parsed_output": None,
                "is_event": False,
                "error_code": res.error_code,
                "inference_time_ms": res.inference_time_ms,
            }
            try:
                self.db.save_analysis_result(article_id, job_id, analysis_dict)
            except Exception as e:
                logger.error(f"Failed to record analysis error for article {article_id}: {e}")
            return True

        # 推論成功 ➔ 保存処理
        parsed_obj = res.parsed_output
        analysis_dict = {
            "model_name": self.llm_client.model_name,
            "model_version": self.llm_client.model_version,
            "prompt_version": self.llm_client.prompt_version,
            "raw_output": res.raw_output,
            "parsed_output": parsed_obj.model_dump() if parsed_obj else None,
            "is_event": parsed_obj.is_event if parsed_obj else False,
            "event_type": parsed_obj.event_type if parsed_obj else None,
            "event_country": parsed_obj.event_country if parsed_obj else None,
            "event_region": parsed_obj.event_region if parsed_obj else None,
            "event_city": parsed_obj.event_city if parsed_obj else None,
            "location_name": parsed_obj.location_name if parsed_obj else None,
            "confidence": parsed_obj.confidence if parsed_obj else 0.0,
            "event_time": parsed_obj.event_time if parsed_obj else None,
            "event_time_precision": parsed_obj.event_time_precision if parsed_obj else None,
            "error_code": None,
            "inference_time_ms": res.inference_time_ms,
        }

        analysis_id, event_id = self.db.save_analysis_result(article_id, job_id, analysis_dict)

        if event_id:
            logger.info(f"Successfully created Event #{event_id} from Article #{article_id} (Type: {parsed_obj.event_type}, Country: {parsed_obj.event_country})")
        else:
            logger.info(f"Article #{article_id} analyzed: is_event=False (No event created)")

        return True

    def run_once(self) -> int:
        """Stale Recovery と全滞留ジョブの順次処理を1周分実行します"""
        # 1. Stale Recovery
        recovered = self.db.recover_stale_jobs(timeout_minutes=self.stale_timeout_minutes)
        if recovered > 0:
            logger.info(f"Recovered {recovered} stale jobs back to 'pending'")

        processed_count = 0
        while self.process_next_job():
            processed_count += 1

        return processed_count

    def start_loop(self):
        """ワーカーメインループ開始"""
        self.running = True
        logger.info(f"Starting ArticleAnalyzerWorker (Poll Interval: {self.poll_interval_seconds}s)")

        while self.running:
            try:
                processed = self.run_once()
                if processed == 0:
                    time.sleep(self.poll_interval_seconds)
            except KeyboardInterrupt:
                logger.info("Received shutdown signal. Stopping worker...")
                self.running = False
            except Exception as e:
                logger.error(f"Error in worker loop: {e}", exc_info=True)
                time.sleep(self.poll_interval_seconds)

    def stop(self):
        self.running = False
