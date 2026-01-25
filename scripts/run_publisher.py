#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.publisher import Publisher
from src.utils import RunLogger, get_run_date, read_json


def main() -> None:
    run_date = get_run_date()
    collector_path = Path("data") / "collector" / f"{run_date}.json"
    writer_markdown = Path("data") / "writer" / f"{run_date}.md"
    writer_meta = Path("data") / "writer" / f"{run_date}.json"
    logger = RunLogger(Path("logs") / f"{run_date}.log")
    quality_path = Path("data") / "quality" / f"{run_date}.json"

    if not collector_path.exists() or not writer_markdown.exists() or not writer_meta.exists():
        raise SystemExit("Collector or Writer output missing")
    if not quality_path.exists():
        raise SystemExit("Quality output missing")

    payload = read_json(collector_path)
    markdown = writer_markdown.read_text(encoding="utf-8")
    summary = json.loads(writer_meta.read_text(encoding="utf-8"))["summary"]

    quality = read_json(quality_path)
    if not quality.get("pass", False):
        raise SystemExit("Quality gate failed")

    sources = []
    for item in payload.get("items", []):
        sources.extend(item.get("sources", []))

    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    try:
        logger.log("Publisher start")
        result = Publisher().publish(
            run_date=run_date,
            markdown_body=markdown,
            summary=summary,
            sources=sources,
            dry_run=dry_run,
        )
        logger.log(f"Publisher done: {result['status']}")
    except Exception as exc:  # noqa: BLE001
        logger.log(f"Publisher failed: {exc}")
        raise


if __name__ == "__main__":
    main()
