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
    markdown_body, summary = _write_with_retry(writer, payload, logger)

    logger.log("Quality gate start")
    quality_result = gate.validate(markdown_body, payload)
    write_json(quality_path, quality_result)

    if not quality_result["pass"]:
        logger.log(f"Quality gate failed: {quality_result['reasons']}")
        raise SystemExit("Quality gate failed")

    logger.log("Publisher start")
    sources = _flatten_sources(payload)
    publish_result = publisher.publish(
        run_date=run_date,
        markdown_body=markdown_body,
        summary=summary,
        sources=sources,
        dry_run=dry_run,
    )

    logger.log(f"Publisher result: {publish_result['status']}")
    logger.log("Pipeline done")
    return {
        "collector": payload,
        "quality": quality_result,
        "publish": publish_result,
    }


def _collect_with_retry(
    collector: Collector,
    run_date: str,
    logger: RunLogger,
    collector_path: Path,
    retries: int = 2,
) -> Dict[str, Any]:
    if collector_path.exists():
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

    raise RuntimeError(f"Collector failed after retries: {last_error}")


def _write_with_retry(
    writer: CopilotWriter,
    payload: Dict[str, Any],
    logger: RunLogger,
    retries: int = 1,
) -> tuple[str, str]:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            logger.log(f"Writer attempt {attempt + 1}")
            return writer.write(payload)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.log(f"Writer error: {exc}")
    raise RuntimeError(f"Writer failed after retries: {last_error}")


def _flatten_sources(payload: Dict[str, Any]) -> list[Dict[str, Any]]:
    sources = []
    for item in payload.get("items", []):
        sources.extend(item.get("sources", []))
    return sources


def main() -> None:
    run_date = get_run_date()
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    run_pipeline(run_date, dry_run=dry_run)


if __name__ == "__main__":
    main()
