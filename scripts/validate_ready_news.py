#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from src.publisher.ready_news import load_ready_items

    ready_root = ROOT / "data" / "ready-news"
    if not ready_root.exists():
        print("[validate-ready-news] skip: data/ready-news does not exist")
        return 0

    date_dirs = sorted(p for p in ready_root.iterdir() if p.is_dir())
    if not date_dirs:
        print("[validate-ready-news] skip: no date directories found")
        return 0

    total_items = 0
    for date_dir in date_dirs:
        run_date = date_dir.name
        items = load_ready_items(ready_dir=ready_root, run_date=run_date)
        total_items += len(items)

    print(
        f"[validate-ready-news] ok: validated {total_items} items in {len(date_dirs)} date directories"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
