from __future__ import annotations

from typing import Dict, Any, List

from .base import Collector
from .local import LocalCollector
from .openweather import OpenWeatherCollector
from .yahoo import YahooFinanceCollector


class _FilteredCollector(Collector):
    def __init__(self, source: Collector, category: str) -> None:
        self.source = source
        self.category = category

    def collect(self, run_date: str) -> Dict[str, Any]:
        payload = self.source.collect(run_date)
        items: List[Dict[str, Any]] = []
        for item in payload.get("items", []):
            if _category_for(item.get("type", "news")) == self.category:
                items.append(item)
        return {"date": payload.get("date", run_date), "items": items}


class MarketCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(YahooFinanceCollector(), "market")


class WeatherCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(OpenWeatherCollector(), "weather")


class LifestyleCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(OpenWeatherCollector(), "life")


class HeadlineCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(LocalCollector(), "news")


def _category_for(item_type: str) -> str:
    mapping = {
        "market": "market",
        "weather": "weather",
        "lifestyle": "life",
        "headline": "news",
    }
    return mapping.get(item_type, "news")
