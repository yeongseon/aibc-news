import time
from typing import Dict, Any

from .base import Collector
from .schema import validate_payload


def collect_with_retry(
    collector: Collector,
    run_date: str,
    retries: int = 2,
    sleep_seconds: int = 600,
    logger=None,
) -> Dict[str, Any]:
    last_error = None
    for attempt in range(retries + 1):
        try:
            if logger:
                logger.log(f"Collector attempt {attempt + 1}")
            payload = collector.collect(run_date)
            validate_payload(payload)
            return payload
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if logger:
                logger.log(f"Collector error: {exc}")
            if attempt < retries:
                time.sleep(sleep_seconds)

    raise RuntimeError(f"Collector failed after retries: {last_error}")
