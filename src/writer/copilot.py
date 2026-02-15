from __future__ import annotations

import os
from typing import Dict, Any, Tuple

import requests

import re

from ..config import GITHUB_MODELS_CHAT_URL, GITHUB_MODELS_MODEL, MIN_CHARS
from .simple import SimpleWriter

SYSTEM_PROMPT = """You are a newsroom writer. Write neutral, broadcast-style Korean news articles.
Follow the constraints strictly:
- 1 item only.
- EXACTLY 2~3 sentences.
- If you include numbers, add '발표일 YYYY-MM-DD' or '기준시점 YYYY-MM-DD'.
- No sensational or opinionated language.
Return ONLY the sentences (no numbering, no title).
"""


class CopilotWriter:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or GITHUB_MODELS_MODEL

    def write_item(self, item: Dict[str, Any], run_date: str) -> Tuple[str, str]:
        api_key = os.environ.get("GITHUB_TOKEN")
        if not api_key:
            raise RuntimeError("GITHUB_TOKEN is not set")

        user_prompt = (
            "다음 JSON 한 건을 참고해 200자 내외 기사 요약을 작성하세요.\n"
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

        normalized = self._normalize(content, item, run_date)
        summary = "오늘의 핵심 이슈 요약"
        return normalized, summary

    def _normalize(self, content: str, collector_payload: Dict[str, Any], run_date: str) -> str:
        text = " ".join(line.strip() for line in content.splitlines() if line.strip())
        text = re.sub(r"^\d+\)\s*", "", text)

        sentences = re.findall(r"[^.!?]+[.!?]", text)
        trimmed = "".join(sentences[:3]).strip() if sentences else text.strip()
        if not trimmed:
            fallback_body, _ = SimpleWriter().write(collector_payload)
            return fallback_body

        has_number = bool(re.search(r"\d", trimmed))
        has_date = bool(re.search(r"\d{4}-\d{2}-\d{2}", trimmed))
        has_marker = "기준시점" in trimmed or "발표일" in trimmed
        if has_number and not (has_date or has_marker):
            trimmed = f"{trimmed} 기준시점 {run_date} 기준입니다."

        base_sentences = re.findall(r"[^.!?]+[.!?]", trimmed)
        if len(base_sentences) < 2:
            trimmed = f"{trimmed} 시장 흐름 점검이 필요합니다."
        elif len(base_sentences) > 3:
            trimmed = "".join(base_sentences[:3]).strip()

        body = "## 오늘의 주요 이슈\n\n" + trimmed + "\n"
        if len(body.replace("\n", "")) < MIN_CHARS:
            additions = [
                "단기 변동성에도 유의해야 합니다.",
                "발표 내용의 후속 변화를 함께 살펴볼 필요가 있습니다.",
            ]
            for extra in additions:
                if len(body.replace("\n", "")) >= MIN_CHARS:
                    break
                trimmed = f"{trimmed} {extra}"
                body = "## 오늘의 주요 이슈\n\n" + trimmed + "\n"
        return body
