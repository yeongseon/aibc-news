from __future__ import annotations

from typing import Dict, Any, List

import yfinance as yf

from .base import Collector
from ..config import YAHOO_SYMBOLS


class YahooFinanceCollector(Collector):
    def collect(self, run_date: str) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []

        for entry in YAHOO_SYMBOLS:
            symbol = entry["symbol"]
            label = entry["label"]

            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get("regularMarketPrice")
            previous = info.get("regularMarketPreviousClose")
            currency = info.get("currency", "")
            market_time = info.get("regularMarketTime")

            facts = []
            if price is not None:
                facts.append(f"현재값 {price} {currency}".strip())
            if previous is not None:
                facts.append(f"전일 종가 {previous} {currency}".strip())
            if market_time:
                facts.append("최근 기준시점 기준")

            if not facts:
                facts.append("최근 가격 변동 요약")

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
