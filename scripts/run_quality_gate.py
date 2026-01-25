#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.quality import QualityGate
from src.utils import RunLogger, get_run_date, read_json, write_json


def main() -> None:
    run_date = get_run_date()
    collector_path = Path("data") / "collector" / f"{run_date}.json"
    writer_markdown = Path("data") / "writer" / f"{run_date}.md"
    quality_path = Path("data") / "quality" / f"{run_date}.json"
    logger = RunLogger(Path("logs") / f"{run_date}.log")

    if not collector_path.exists() or not writer_markdown.exists():
        raise SystemExit("Collector or Writer output missing")

    logger.log("Quality gate start")
    payload = read_json(collector_path)
    markdown = writer_markdown.read_text(encoding="utf-8")
    result = QualityGate().validate(markdown, payload)
    write_json(quality_path, result)
    logger.log("Quality gate done")

    if not result["pass"]:
        raise SystemExit("Quality gate failed")


if __name__ == "__main__":
    main()
