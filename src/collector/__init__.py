from .local import LocalCollector
from .yahoo import YahooFinanceCollector
from .openweather import OpenWeatherCollector
from .composite import CompositeCollector
from .category import MarketCollector, WeatherCollector, LifestyleCollector, HeadlineCollector

__all__ = [
    "LocalCollector",
    "YahooFinanceCollector",
    "OpenWeatherCollector",
    "CompositeCollector",
    "MarketCollector",
    "WeatherCollector",
    "LifestyleCollector",
    "HeadlineCollector",
]
