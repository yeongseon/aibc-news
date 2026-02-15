from typing import Dict, Any, List

from .base import Collector


class LocalCollector(Collector):
    def collect(self, run_date: str) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = [
            {
                "type": "politics",
                "title": "정부, AI 산업 지원 계획 발표",
                "facts": [
                    "AI 연구개발 예산 확대",
                    "스타트업 지원 펀드 신설",
                ],
                "sources": [
                    {
                        "name": "과학기술정보통신부",
                        "url": "https://example.com/msit-ai-plan",
                        "published_at": run_date,
                    }
                ],
            },
            {
                "type": "economy",
                "title": "코스피, AI 관련주 강세",
                "facts": [
                    "AI 반도체 종목 상승",
                    "거래량 증가",
                ],
                "sources": [
                    {
                        "name": "한국거래소",
                        "url": "https://example.com/krx-ai-market",
                        "published_at": run_date,
                    }
                ],
            },
            {
                "type": "society",
                "title": "디지털 민원 서비스 확대",
                "facts": [
                    "온라인 민원 창구 확대",
                    "처리 기간 단축",
                ],
                "sources": [
                    {
                        "name": "행정안전부",
                        "url": "https://example.com/mois-service",
                        "published_at": run_date,
                    }
                ],
            },
            {
                "type": "world",
                "title": "주요국 AI 규제 논의 확대",
                "facts": [
                    "글로벌 기준안 마련 논의",
                    "투명성 요구 강화",
                ],
                "sources": [
                    {
                        "name": "UNESCO",
                        "url": "https://example.com/unesco-ai",
                        "published_at": run_date,
                    }
                ],
            },
            {
                "type": "tech",
                "title": "차세대 반도체 연구 성과 공개",
                "facts": [
                    "저전력 칩셋 개발",
                    "생산성 개선 기대",
                ],
                "sources": [
                    {
                        "name": "ETRI",
                        "url": "https://example.com/etri-chip",
                        "published_at": run_date,
                    }
                ],
            },
            {
                "type": "culture",
                "title": "지역 문화행사 확대",
                "facts": [
                    "지역 축제 일정 발표",
                    "문화예술 참여 확대",
                ],
                "sources": [
                    {
                        "name": "문화체육관광부",
                        "url": "https://example.com/mcst-culture",
                        "published_at": run_date,
                    }
                ],
            },
            {
                "type": "sports",
                "title": "프로리그 일정 공개",
                "facts": [
                    "개막전 대진 발표",
                    "관중 수용 확대",
                ],
                "sources": [
                    {
                        "name": "대한체육회",
                        "url": "https://example.com/koc-schedule",
                        "published_at": run_date,
                    }
                ],
            },
            {
                "type": "entertainment",
                "title": "신작 드라마 공개 일정 발표",
                "facts": [
                    "주요 플랫폼 라인업 공개",
                    "콘텐츠 경쟁 강화",
                ],
                "sources": [
                    {
                        "name": "한국콘텐츠진흥원",
                        "url": "https://example.com/kocca-drama",
                        "published_at": run_date,
                    }
                ],
            },
            {
                "type": "weather",
                "title": "전국 한파 특보 유지",
                "facts": [
                    "아침 최저기온 영하권",
                    "강풍 및 건조 주의",
                ],
                "sources": [
                    {
                        "name": "기상청",
                        "url": "https://example.com/kma-cold-wave",
                        "published_at": run_date,
                    }
                ],
            },
            {
                "type": "life",
                "title": "실내 공기질 관리 필요",
                "facts": [
                    "미세먼지 농도 상승",
                    "환기 시간 조정 권고",
                ],
                "sources": [
                    {
                        "name": "환경부",
                        "url": "https://example.com/moe-air-guide",
                        "published_at": run_date,
                    }
                ],
            },
        ]

        return {
            "date": run_date,
            "items": items,
        }
