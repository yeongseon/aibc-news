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
            if _category_for(item.get("type", "politics")) == self.category:
                items.append(item)
        return {"date": payload.get("date", run_date), "items": items}


class EconomyCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(YahooFinanceCollector(), "economy")


class WeatherCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(OpenWeatherCollector(), "weather")


class LifeCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(OpenWeatherCollector(), "life")


class PoliticsCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(LocalCollector(), "politics")


class SocietyCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(LocalCollector(), "society")


class WorldCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(LocalCollector(), "world")


class TechCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(LocalCollector(), "tech")


class CultureCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(LocalCollector(), "culture")


class SportsCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(LocalCollector(), "sports")


class EntertainmentCollector(_FilteredCollector):
    def __init__(self) -> None:
        super().__init__(LocalCollector(), "entertainment")


def _category_for(item_type: str) -> str:
    mapping = {
        "politics": "politics",
        "economy": "economy",
        "society": "society",
        "world": "world",
        "tech": "tech",
        "culture": "culture",
        "sports": "sports",
        "entertainment": "entertainment",
        "life": "life",
        "weather": "weather",
    }
    return mapping.get(item_type, "politics")
