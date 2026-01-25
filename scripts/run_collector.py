#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.collector import LocalCollector
from src.utils import RunLogger, ensure_dir, get_run_date, write_json


def main() -> None:
    run_date = get_run_date()
    collector_path = Path("data") / "collector" / f"{run_date}.json"
    logger = RunLogger(Path("logs") / f"{run_date}.log")
    ensure_dir(collector_path.parent)

    if collector_path.exists():
        logger.log("Collector skip: already exists")
        return

    try:
        logger.log("Collector start")
        payload = LocalCollector().collect(run_date)
        write_json(collector_path, payload)
        logger.log("Collector done")
    except Exception as exc:  # noqa: BLE001
        logger.log(f"Collector failed: {exc}")
        raise


if __name__ == "__main__":
    main()
