#!/usr/bin/env python3
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.publisher import load_ready_items, publish_ready_items
from src.utils import get_run_date


def main() -> None:
    run_date = get_run_date()
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    category = os.environ.get("PIPELINE_KIND") or os.environ.get("CATEGORY")
    force_publish = os.environ.get("FORCE_PUBLISH", "false").lower() == "true"
    ready_dir = Path(os.environ.get("READY_NEWS_DIR", "data/ready-news"))

    items = load_ready_items(ready_dir=ready_dir, run_date=run_date, category=category)
    publish_ready_items(items, dry_run=dry_run, force=force_publish)


if __name__ == "__main__":
    main()
