from __future__ import annotations

import os
from typing import Dict, Any, Tuple

import requests

from ..config import GITHUB_MODELS_CHAT_URL, GITHUB_MODELS_MODEL

SYSTEM_PROMPT = """You are a newsroom writer. Write neutral, broadcast-style Korean news briefs.
Follow the constraints strictly:
- 3~5 items, each EXACTLY 3 sentences.
- Include context/insight within those 3 sentences.
- If you include numbers, add '발표일 YYYY-MM-DD' or '기준시점 YYYY-MM-DD'.
- No sensational or opinionated language.
Return ONLY markdown body (no front matter).
Output format must follow EXACTLY:
## 오늘의 주요 이슈

1) ...
...

2) ...
...

3) ...
...
"""


class CopilotWriter:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or GITHUB_MODELS_MODEL

    def write(self, collector_payload: Dict[str, Any]) -> Tuple[str, str]:
        api_key = os.environ.get("GITHUB_TOKEN")
        if not api_key:
            raise RuntimeError("GITHUB_TOKEN is not set")

        run_date = collector_payload.get("date", "")
        user_prompt = (
            "다음 JSON을 참고해 오늘의 브리핑을 작성하세요.\n"
            "각 항목에는 '발표일 YYYY-MM-DD' 또는 '기준시점 YYYY-MM-DD'를 반드시 포함하세요.\n"
            "항목 제목은 [시장]/[날씨] 등으로 시작해도 됩니다.\n\n"
            f"발행일: {run_date}\n"
            f"JSON: {collector_payload}"
        )

        response = requests.post(
            GITHUB_MODELS_CHAT_URL,
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
