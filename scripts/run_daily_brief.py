#!/usr/bin/env python3
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import run_pipeline
from src.utils import get_run_date


def main() -> None:
    run_date = get_run_date()
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    category = os.environ.get("CATEGORY")
    run_pipeline(run_date, dry_run=dry_run, category=category)


if __name__ == "__main__":
    main()
