from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

from ..domain.models import CollectorPayload
from ..app import generate_posts, publish_posts, QualityGateError
from .ports import CollectorPort, LoggerPort, PublisherPort, QualityPort, WriterPort


class RunDailyBriefUseCase:
    def __init__(
        self,
        collector: CollectorPort,
        writer: WriterPort,
        gate: QualityPort,
        publisher: PublisherPort,
        logger: LoggerPort,
        *,
        collector_retries: int = 2,
        writer_retries: int = 1,
    ):
        self.collector = collector
        self.writer = writer
        self.gate = gate
        self.publisher = publisher
        self.logger = logger
        self.collector_retries = collector_retries
        self.writer_retries = writer_retries

    def execute(
        self,
        run_date: str,
        *,
        collector_path: Path,
        quality_path: Path,
        dry_run: bool,
        force_collect: bool = False,
        force_publish: bool = False,
        category: str | None = None,
        read_json,
        write_json,
    ) -> Dict[str, Any]:
        payload = self._collect_with_retry(
            run_date,
            collector_path,
            force_collect=force_collect,
            read_json=read_json,
            write_json=write_json,
        )
        class _RetryWriter:
            def __init__(self, parent: "RunDailyBriefUseCase"):
                self.parent = parent

            def write_item(self, item, run_date: str):
                return self.parent._write_item_with_retry(item, run_date)

        if category:
            payload = self._filter_payload(payload, category)

        try:
            drafts, quality_results = generate_posts(
                payload,
                run_date,
                writer=_RetryWriter(self),
                gate=self.gate,
                logger=self.logger,
            )
        except QualityGateError as exc:
            write_json(
                quality_path,
                {
                    "run_date": run_date,
                    "items": exc.quality_results,
                },
            )
            raise SystemExit("Quality gate failed") from exc

        results = publish_posts(
            drafts,
            publisher=self.publisher,
            dry_run=dry_run,
            force=force_publish,
        )

        write_json(
            quality_path,
            {
                "run_date": run_date,
                "items": quality_results,
            },
        )

        return {
            "collector": payload,
            "publish": results,
        }

    def _collect_with_retry(
        self,
        run_date: str,
        collector_path: Path,
        force_collect: bool,
        read_json,
        write_json,
    ) -> Dict[str, Any]:
        if collector_path.exists() and not force_collect:
            self.logger.log("Collector cache hit")
            return read_json(collector_path)

        last_error: Exception | None = None
        for attempt in range(self.collector_retries + 1):
            try:
                self.logger.log(f"Collector attempt {attempt + 1}")
                payload = self.collector.collect(run_date)
                write_json(collector_path, payload)
                return payload
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                self.logger.log(f"Collector error: {exc}")
                if attempt < self.collector_retries:
                    backoff = 15 * (attempt + 1)
                    self.logger.log(f"Collector retry in {backoff}s")
                    time.sleep(backoff)

        raise RuntimeError(f"Collector failed after retries: {last_error}")

    def _write_item_with_retry(
        self, item: Dict[str, Any], run_date: str
    ) -> tuple[str, str]:
        last_error: Exception | None = None
        for attempt in range(self.writer_retries + 1):
            try:
                self.logger.log(f"Writer attempt {attempt + 1}")
                return self.writer.write_item(item, run_date)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                self.logger.log(f"Writer error: {exc}")
                if attempt < self.writer_retries:
                    backoff = 10 * (attempt + 1)
                    self.logger.log(f"Writer retry in {backoff}s")
                    time.sleep(backoff)
        raise RuntimeError(f"Writer failed after retries: {last_error}")

    def _validate_quality(
        self, markdown_body: str, item_payload: Dict[str, Any]
    ) -> Dict[str, Any] | Any:
        self.logger.log("Quality gate start")
        return self.gate.validate(markdown_body, {"items": [item_payload]})

    @staticmethod
    def _filter_payload(payload: Dict[str, Any], category: str) -> Dict[str, Any]:
        def _category_for(item_type: str) -> str:
            mapping = {
                "politics": "politics",
                "economy": "economy",
                "society": "society",
                "world": "world",
                "tech": "tech",
                "culture": "culture",
                "sports": "sports",
                "entertainment": "entertainment",
                "life": "life",
                "weather": "weather",
            }
            return mapping.get(item_type, "politics")

        filtered_items = [
            item
            for item in payload.get("items", [])
            if _category_for(item.get("type", "politics")) == category
        ]
        return {
            "date": payload.get("date", ""),
            "items": filtered_items,
        }

    @staticmethod
    def _slug_for(item_type: str) -> str:
        mapping = {
            "politics": "politics",
            "economy": "economy",
            "society": "society",
            "world": "world",
            "tech": "tech",
            "culture": "culture",
            "sports": "sports",
            "entertainment": "entertainment",
            "life": "life",
            "weather": "weather",
        }
        return mapping.get(item_type, "politics")
