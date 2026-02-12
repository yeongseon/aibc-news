from __future__ import annotations

from typing import Dict, Any, List

import requests

from .base import Collector
from ..config import YAHOO_SYMBOLS


class YahooFinanceCollector(Collector):
    def collect(self, run_date: str) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []

        symbols = [entry["symbol"] for entry in YAHOO_SYMBOLS]
        response = requests.get(
            "https://query1.finance.yahoo.com/v7/finance/quote",
            params={"symbols": ",".join(symbols)},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        if response.status_code == 429:
            raise RuntimeError("Yahoo Finance rate limited (HTTP 429)")
        response.raise_for_status()

        payload = response.json()
        results = payload.get("quoteResponse", {}).get("result", [])
        by_symbol = {item.get("symbol"): item for item in results}

        if not by_symbol:
            raise RuntimeError("Yahoo Finance returned no data")

        for entry in YAHOO_SYMBOLS:
            symbol = entry["symbol"]
            label = entry["label"]
            data = by_symbol.get(symbol, {})

            current = data.get("regularMarketPrice")
            previous = data.get("regularMarketPreviousClose")
            currency = data.get("currency", "")

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

        return {"date": run_date, "items": items}
