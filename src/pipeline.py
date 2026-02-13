import os
from pathlib import Path
from typing import Dict, Any

from .collector import CompositeCollector
from .collector.base import Collector
from .publisher import Publisher
from .quality import QualityGate
from .utils import RunLogger, ensure_dir, get_run_date, read_json, write_json
from .writer import CopilotWriter


def run_pipeline(run_date: str, dry_run: bool = False) -> Dict[str, Any]:
    data_dir = Path("data")
    logs_dir = Path("logs")
    ensure_dir(data_dir)
    ensure_dir(logs_dir)

    logger = RunLogger(logs_dir / f"{run_date}.log")
    logger.log("Pipeline start")

    collector_path = data_dir / "collector" / f"{run_date}.json"
    quality_path = data_dir / "quality" / f"{run_date}.json"

    collector = CompositeCollector()
    writer = CopilotWriter()
    gate = QualityGate()
    publisher = Publisher()

    payload = _collect_with_retry(collector, run_date, logger, collector_path)

    logger.log("Writer start")
    per_item_results = []

    for item in payload.get("items", []):
        markdown_body, summary = _write_item(writer, item, run_date, logger)

        logger.log("Quality gate start")
        quality_result = gate.validate(markdown_body, {"items": [item]})
        write_json(quality_path, quality_result)

        if not quality_result["pass"]:
            logger.log(f"Quality gate failed: {quality_result['reasons']}")
            raise SystemExit("Quality gate failed")

        logger.log("Publisher start")
        sources = item.get("sources", [])
        category, slug = _category_for(item)
        publish_result = publisher.publish(
            run_date=run_date,
            markdown_body=markdown_body,
            summary=summary,
            sources=sources,
            category=category,
            slug_suffix=slug,
            dry_run=dry_run,
        )

        per_item_results.append(
            {
                "item": item,
                "quality": quality_result,
                "publish": publish_result,
            }
        )
        logger.log(f"Publisher result: {publish_result['status']}")

    logger.log("Pipeline done")
    return {
        "collector": payload,
        "publish": per_item_results,
    }


def _collect_with_retry(
    collector: Collector,
    run_date: str,
    logger: RunLogger,
    collector_path: Path,
    retries: int = 2,
) -> Dict[str, Any]:
    force_collect = os.environ.get("FORCE_COLLECT", "false").lower() == "true"
    if collector_path.exists() and not force_collect:
        logger.log("Collector cache hit")
        return read_json(collector_path)

    last_error = None
    for attempt in range(retries + 1):
        try:
            logger.log(f"Collector attempt {attempt + 1}")
            payload = collector.collect(run_date)
            write_json(collector_path, payload)
            return payload
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.log(f"Collector error: {exc}")
            if attempt < retries:
                backoff = 10 * (attempt + 1)
                logger.log(f"Collector retry in {backoff}s")
                import time

                time.sleep(backoff)

    raise RuntimeError(f"Collector failed after retries: {last_error}")


def _write_item(
    writer: CopilotWriter,
    item: Dict[str, Any],
    run_date: str,
    logger: RunLogger,
    retries: int = 1,
) -> tuple[str, str]:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            logger.log(f"Writer attempt {attempt + 1}")
            return writer.write_item(item, run_date)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.log(f"Writer error: {exc}")
    raise RuntimeError(f"Writer failed after retries: {last_error}")


def _category_for(item: Dict[str, Any]) -> tuple[str, str]:
    item_type = item.get("type", "news")
    mapping = {
        "market": ("market", "market"),
        "weather": ("weather", "weather"),
        "lifestyle": ("life", "life"),
        "headline": ("news", "news"),
    }
    return mapping.get(item_type, ("news", "news"))


def main() -> None:
    run_date = get_run_date()
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    run_pipeline(run_date, dry_run=dry_run)


if __name__ == "__main__":
    main()
