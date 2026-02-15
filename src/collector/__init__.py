from .local import LocalCollector
from .yahoo import YahooFinanceCollector
from .openweather import OpenWeatherCollector
from .composite import CompositeCollector
from .category import (
    EconomyCollector,
    WeatherCollector,
    LifeCollector,
    PoliticsCollector,
    SocietyCollector,
    WorldCollector,
    TechCollector,
    CultureCollector,
    SportsCollector,
    EntertainmentCollector,
)

__all__ = [
    "LocalCollector",
    "YahooFinanceCollector",
    "OpenWeatherCollector",
    "CompositeCollector",
    "EconomyCollector",
    "WeatherCollector",
    "LifeCollector",
    "PoliticsCollector",
    "SocietyCollector",
    "WorldCollector",
    "TechCollector",
    "CultureCollector",
    "SportsCollector",
    "EntertainmentCollector",
]
