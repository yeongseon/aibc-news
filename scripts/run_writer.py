#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils import RunLogger, ensure_dir, get_run_date, read_json
from src.writer import SimpleWriter, validate_writer_output


def main() -> None:
    run_date = get_run_date()
    collector_path = Path("data") / "collector" / f"{run_date}.json"
    writer_dir = Path("data") / "writer"
    writer_markdown = writer_dir / f"{run_date}.md"
    writer_meta = writer_dir / f"{run_date}.json"
    logger = RunLogger(Path("logs") / f"{run_date}.log")
    ensure_dir(writer_dir)

    if writer_markdown.exists() and writer_meta.exists():
        logger.log("Writer skip: already exists")
        return

    if not collector_path.exists():
        raise SystemExit("Collector output missing")

    with logger.step("Writer"):
        payload = read_json(collector_path)
        body, summary = SimpleWriter().write(payload)
        validate_writer_output(body)
        writer_markdown.write_text(body, encoding="utf-8")
        writer_meta.write_text(
            json.dumps({"summary": summary}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
