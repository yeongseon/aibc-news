from __future__ import annotations

import os
from typing import Dict, Any, List

import requests

from .base import Collector
from ..config import (
    OPENWEATHER_BASE_URL,
    OPENWEATHER_CITIES,
    OPENWEATHER_UNITS,
    OPENWEATHER_LANG,
)


class OpenWeatherCollector(Collector):
    def collect(self, run_date: str) -> Dict[str, Any]:
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENWEATHER_API_KEY is not set")

        city_payloads = []
        for city in OPENWEATHER_CITIES:
            params = {
                "q": city,
                "appid": api_key,
                "units": OPENWEATHER_UNITS,
                "lang": OPENWEATHER_LANG,
            }
            response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            city_payloads.append(response.json())

        temps = []
        winds = []
        humidities = []
        descriptions: List[str] = []
        city_facts: List[str] = []

        for payload in city_payloads:
            city = payload.get("name", "도시")
            weather = payload.get("weather", [{}])[0]
            main = payload.get("main", {})
            wind = payload.get("wind", {})

            description = weather.get("description", "날씨 요약")
            temp = main.get("temp")
            humidity = main.get("humidity")
            wind_speed = wind.get("speed")

            if temp is not None:
                temps.append(temp)
            if humidity is not None:
                humidities.append(humidity)
            if wind_speed is not None:
                winds.append(wind_speed)
            if description:
                descriptions.append(description)

            city_bits = [f"{city}: {description}"]
            if temp is not None:
                city_bits.append(f"{temp}°C")
            if wind_speed is not None:
                city_bits.append(f"풍속 {wind_speed}m/s")
            city_facts.append(" ".join(city_bits))

        avg_temp = sum(temps) / len(temps) if temps else None
        max_wind = max(winds) if winds else None
        avg_humidity = sum(humidities) / len(humidities) if humidities else None

        summary_bits = ["전국 요약: 주요 도시 기준"]
        if avg_temp is not None:
            summary_bits.append(f"평균 기온 {avg_temp:.1f}°C")
        if avg_humidity is not None:
            summary_bits.append(f"평균 습도 {avg_humidity:.0f}%")
        if max_wind is not None:
            summary_bits.append(f"최대 풍속 {max_wind:.1f}m/s")
        if descriptions:
            summary_bits.append(f"전반적 상태 {descriptions[0]}")

        facts: List[str] = [" ".join(summary_bits)]
        facts.extend(city_facts)

        weather_item = {
            "type": "weather",
            "title": "전국 및 주요 도시 날씨",
            "facts": facts,
            "slug": "kr",
            "sources": [
                {
                    "name": "OpenWeather",
                    "url": "https://openweathermap.org",
                    "published_at": run_date,
                }
            ],
        }

        lifestyle_item = {
            "type": "lifestyle",
            "title": "체감 환경 요약",
            "facts": [
                "전국 평균 체감 환경은 지역별 편차가 있으니 이동 계획을 점검하세요.",
                "실내외 온도 차와 습도 변화에 유의할 필요가 있습니다.",
            ],
            "slug": "kr-env",
            "sources": [
                {
                    "name": "OpenWeather",
                    "url": "https://openweathermap.org",
                    "published_at": run_date,
                }
            ],
        }

        return {"date": run_date, "items": [weather_item, lifestyle_item]}
