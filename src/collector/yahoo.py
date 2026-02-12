from __future__ import annotations

from typing import Dict, Any, List

import requests

from .base import Collector
from ..config import YAHOO_SYMBOLS


class YahooFinanceCollector(Collector):
    def collect(self, run_date: str) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []

        for entry in YAHOO_SYMBOLS:
            symbol = entry["symbol"]
            label = entry["label"]

            response = requests.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                params={"interval": "1d", "range": "5d"},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15,
            )
            if response.status_code == 429:
                raise RuntimeError("Yahoo Finance rate limited (HTTP 429)")
            response.raise_for_status()

            payload = response.json()
            result = payload.get("chart", {}).get("result", [None])[0]
            if not result:
                raise RuntimeError("Yahoo Finance returned no data")

            indicators = result.get("indicators", {}).get("quote", [{}])[0]
            closes = [c for c in (indicators.get("close") or []) if c is not None]
            current = closes[-1] if closes else None
            previous = closes[-2] if len(closes) > 1 else None
            currency = result.get("meta", {}).get("currency", "")

            facts = []
            if current is not None:
                facts.append(f"현재값 {current} {currency}".strip())
            if previous is not None:
                facts.append(f"전일 종가 {previous} {currency}".strip())
            facts.append("최근 기준시점 기준")

            items.append(
                {
                    "type": "market",
                    "title": f"{label} 최신 흐름",
                    "facts": facts,
                    "sources": [
                        {
                            "name": "Yahoo Finance",
                            "url": f"https://finance.yahoo.com/quote/{symbol}",
                            "published_at": run_date,
                        }
                    ],
                }
            )

        if not items:
            raise RuntimeError("Yahoo Finance returned no data")

        return {"date": run_date, "items": items}
