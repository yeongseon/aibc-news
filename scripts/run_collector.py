#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import os

from src.collector import LocalCollector, collect_with_retry
from src.utils import RunLogger, ensure_dir, get_run_date, write_json


def main() -> None:
    run_date = get_run_date()
    collector_path = Path("data") / "collector" / f"{run_date}.json"
    logger = RunLogger(Path("logs") / f"{run_date}.log")
    ensure_dir(collector_path.parent)

    if collector_path.exists():
        logger.log("Collector skip: already exists")
        return

    with logger.step("Collector"):
        sleep_seconds = int(os.environ.get("RETRY_SLEEP_SECONDS", "600"))
        payload = collect_with_retry(
            LocalCollector(),
            run_date,
            retries=2,
            sleep_seconds=sleep_seconds,
            logger=logger,
        )
        write_json(collector_path, payload)


if __name__ == "__main__":
    main()
