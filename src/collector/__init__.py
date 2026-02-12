from .local import LocalCollector
from .yahoo import YahooFinanceCollector
from .openweather import OpenWeatherCollector
from .composite import CompositeCollector

__all__ = [
    "LocalCollector",
    "YahooFinanceCollector",
    "OpenWeatherCollector",
    "CompositeCollector",
]
