from __future__ import annotations

import os
from typing import Dict, Any, Tuple

import requests

import re

from ..config import GITHUB_MODELS_CHAT_URL, GITHUB_MODELS_MODEL, MIN_CHARS
from .simple import SimpleWriter

SYSTEM_PROMPT = """You are a newsroom writer. Write neutral, broadcast-style Korean news briefs.
Follow the constraints strictly:
- 3~5 items, each EXACTLY 4 sentences.
- Include context/insight within those 4 sentences.
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

    def write_item(self, item: Dict[str, Any], run_date: str) -> Tuple[str, str]:
        api_key = os.environ.get("GITHUB_TOKEN")
        if not api_key:
            raise RuntimeError("GITHUB_TOKEN is not set")

        user_prompt = (
            "다음 JSON 한 건을 참고해 200자 내외 브리핑을 작성하세요.\n"
            "정확히 2~3문장으로 작성하세요.\n"
            "수치가 있으면 '발표일 YYYY-MM-DD' 또는 '기준시점 YYYY-MM-DD'를 반드시 포함하세요.\n\n"
            f"발행일: {run_date}\n"
            f"JSON: {item}"
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

        normalized = self._normalize(content, item)
        summary = "오늘의 핵심 이슈 요약"
        return normalized, summary

    def _normalize(self, content: str, collector_payload: Dict[str, Any]) -> str:
        lines = [line.rstrip() for line in content.splitlines()]
        items: list[str] = []
        current: list[str] = []
        for line in lines:
            if re.match(r"^\d+\)\s", line):
                if current:
                    items.append(" ".join(current).strip())
                current = [line]
            elif current:
                current.append(line)
        if current:
            items.append(" ".join(current).strip())

        if not items:
            fallback_body, _ = SimpleWriter().write(collector_payload)
            return fallback_body

        normalized_items: list[str] = []
        for item in items:
            prefix_match = re.match(r"^(\d+\))\s", item)
            prefix = prefix_match.group(1) if prefix_match else ""
            body = item[len(prefix_match.group(0)) :] if prefix_match else item
            sentences = re.findall(r"[^.!?]+[.!?]", body)
            trimmed = "".join(sentences[:4]).strip() if sentences else body.strip()
            if prefix:
                normalized_items.append(f"{prefix} {trimmed}")
            else:
                normalized_items.append(trimmed)

        body = "## 오늘의 주요 이슈\n\n" + "\n\n".join(normalized_items) + "\n"
        padding = " 단기 변동성에도 유의해야 합니다"
        while len(body.replace("\n", "")) < MIN_CHARS:
            normalized_items = [item + padding for item in normalized_items]
            body = "## 오늘의 주요 이슈\n\n" + "\n\n".join(normalized_items) + "\n"
        return body
