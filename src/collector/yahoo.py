from __future__ import annotations

from typing import Dict, Any, List

import yfinance as yf

from .base import Collector
from ..config import YAHOO_SYMBOLS


class YahooFinanceCollector(Collector):
    def collect(self, run_date: str) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []

        symbols = [entry["symbol"] for entry in YAHOO_SYMBOLS]
        data = yf.download(
            symbols,
            period="2d",
            interval="1d",
            group_by="ticker",
            auto_adjust=False,
            threads=False,
            progress=False,
        )

        if data is None or data.empty:
            raise RuntimeError("Yahoo Finance returned no data")

        for entry in YAHOO_SYMBOLS:
            symbol = entry["symbol"]
            label = entry["label"]

            if symbol in data.columns.get_level_values(0):
                close_series = data[symbol]["Close"].dropna()
            else:
                close_series = data["Close"].dropna()

            closes = close_series.tail(2).tolist()
            current = closes[-1] if closes else None
            previous = closes[-2] if len(closes) > 1 else None

            facts = []
            if current is not None:
                facts.append(f"현재값 {current}")
            if previous is not None:
                facts.append(f"전일 종가 {previous}")
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
