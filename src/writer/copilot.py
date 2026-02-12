from __future__ import annotations

import os
from typing import Dict, Any, Tuple

import requests

from ..config import COPILOT_CHAT_URL, COPILOT_MODEL

SYSTEM_PROMPT = """You are a newsroom writer. Write neutral, broadcast-style Korean news briefs.
Follow the constraints strictly:
- 3~5 items, each 2~4 sentences.
- Include context/insight 2~3 sentences per item.
- If you include numbers, add '발표일 YYYY-MM-DD' or '기준시점 YYYY-MM-DD'.
- No sensational or opinionated language.
Return ONLY markdown body (no front matter).
"""


class CopilotWriter:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or COPILOT_MODEL

    def write(self, collector_payload: Dict[str, Any]) -> Tuple[str, str]:
        api_key = os.environ.get("COPILOT_API_KEY")
        if not api_key:
            raise RuntimeError("COPILOT_API_KEY is not set")

        run_date = collector_payload.get("date", "")
        user_prompt = (
            "다음 JSON을 참고해 오늘의 브리핑을 작성하세요.\n"
            "각 항목에는 '발표일 YYYY-MM-DD' 또는 '기준시점 YYYY-MM-DD'를 반드시 포함하세요.\n\n"
            f"발행일: {run_date}\n"
            f"JSON: {collector_payload}"
        )

        response = requests.post(
            COPILOT_CHAT_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 1200,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()

        choices = payload.get("choices", [])
        if not choices:
            raise RuntimeError("Copilot response missing choices")

        content = choices[0].get("message", {}).get("content")
        if not content:
            raise RuntimeError("Copilot response missing content")

        summary = "오늘의 핵심 이슈 3~5건 요약"
        return content.strip() + "\n", summary
