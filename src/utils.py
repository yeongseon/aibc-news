import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import KST_TZ


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def now_kst_date() -> str:
    return datetime.now(ZoneInfo(KST_TZ)).strftime("%Y-%m-%d")


def get_run_date() -> str:
    env_date = os.environ.get("RUN_DATE", "").strip()
    return env_date or now_kst_date()


class RunLogger:
    def __init__(self, log_path: Path):
        ensure_dir(log_path.parent)
        self.log_path = log_path

    def log(self, message: str) -> None:
        timestamp = datetime.now(ZoneInfo(KST_TZ)).strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}\n"
        self.log_path.write_text(
            self.log_path.read_text(encoding="utf-8") + line
            if self.log_path.exists()
            else line,
            encoding="utf-8",
        )
