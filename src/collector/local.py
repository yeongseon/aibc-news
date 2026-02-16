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
        ]

        return {
            "date": run_date,
            "items": items,
        }
