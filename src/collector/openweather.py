from __future__ import annotations

import os
from typing import Dict, Any, List

import requests

from .base import Collector
from ..config import (
    OPENWEATHER_BASE_URL,
    OPENWEATHER_CITY,
    OPENWEATHER_UNITS,
    OPENWEATHER_LANG,
)


class OpenWeatherCollector(Collector):
    def collect(self, run_date: str) -> Dict[str, Any]:
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENWEATHER_API_KEY is not set")

        params = {
            "q": OPENWEATHER_CITY,
            "appid": api_key,
            "units": OPENWEATHER_UNITS,
            "lang": OPENWEATHER_LANG,
        }
        response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()

        weather = payload.get("weather", [{}])[0]
        main = payload.get("main", {})
        wind = payload.get("wind", {})

        description = weather.get("description", "날씨 요약")
        temp = main.get("temp")
        feels_like = main.get("feels_like")
        humidity = main.get("humidity")
        wind_speed = wind.get("speed")

        facts: List[str] = [description]
        if temp is not None:
            facts.append(f"기온 {temp}°C")
        if feels_like is not None:
            facts.append(f"체감 {feels_like}°C")
        if humidity is not None:
            facts.append(f"습도 {humidity}%")
        if wind_speed is not None:
            facts.append(f"풍속 {wind_speed}m/s")

        weather_item = {
            "type": "weather",
            "title": f"{OPENWEATHER_CITY} 날씨 요약",
            "facts": facts,
            "sources": [
                {
                    "name": "OpenWeather",
                    "url": "https://openweathermap.org",
                    "published_at": run_date,
                }
            ],
        }

        lifestyle_facts: List[str] = []
        if humidity is not None:
            lifestyle_facts.append(f"실내 습도 {humidity}%")
        if wind_speed is not None:
            lifestyle_facts.append(f"바람 {wind_speed}m/s")
        if not lifestyle_facts:
            lifestyle_facts.append("체감 환경 점검 필요")

        lifestyle_item = {
            "type": "lifestyle",
            "title": f"{OPENWEATHER_CITY} 체감 환경",
            "facts": lifestyle_facts,
            "sources": [
                {
                    "name": "OpenWeather",
                    "url": "https://openweathermap.org",
                    "published_at": run_date,
                }
            ],
        }

        return {"date": run_date, "items": [weather_item, lifestyle_item]}
