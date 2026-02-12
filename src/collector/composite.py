from __future__ import annotations

from typing import Dict, Any, List

from .base import Collector
from .openweather import OpenWeatherCollector
from .yahoo import YahooFinanceCollector


class CompositeCollector(Collector):
    def __init__(self) -> None:
        self.market_collector = YahooFinanceCollector()
        self.weather_collector = OpenWeatherCollector()

    def collect(self, run_date: str) -> Dict[str, Any]:
        market_payload = self.market_collector.collect(run_date)
        weather_payload = self.weather_collector.collect(run_date)

        items: List[Dict[str, Any]] = []
        items.extend(market_payload.get("items", []))
        items.extend(weather_payload.get("items", []))

        return {
            "date": run_date,
            "items": items,
        }
