import re
from typing import Dict, Any, List

from ..config import (
    FORBIDDEN_WORDS,
    MAX_CHARS,
    MAX_ITEMS,
    MAX_SINGLE_SOURCE_RATIO,
    MAX_SENTENCES,
    MIN_CHARS,
    MIN_ITEMS,
    MIN_SENTENCES,
    MIN_SOURCES_TOTAL,
)


class QualityGate:
    def validate(self, markdown: str, collector_payload: Dict[str, Any]) -> Dict[str, Any]:
        reasons: List[str] = []

        char_count = len(markdown.replace("\n", ""))
        if not (MIN_CHARS <= char_count <= MAX_CHARS):
            reasons.append(f"분량({char_count})이 기준({MIN_CHARS}-{MAX_CHARS})을 벗어남")

        items = self._split_items(markdown)
        item_count = len(items)
        if not (MIN_ITEMS <= item_count <= MAX_ITEMS):
            reasons.append(f"항목 수({item_count})가 기준({MIN_ITEMS}-{MAX_ITEMS})을 벗어남")

        for idx, item in enumerate(items, start=1):
            sentence_count = self._count_sentences(item)
            if not (MIN_SENTENCES <= sentence_count <= MAX_SENTENCES):
                reasons.append(f"항목 {idx} 문장 수({sentence_count})가 기준({MIN_SENTENCES}-{MAX_SENTENCES})을 벗어남")

            if self._contains_number_without_date(item):
                reasons.append(f"항목 {idx}에 수치가 있으나 기준시점/발표일 표기가 없음")

        if any(word in markdown for word in FORBIDDEN_WORDS):
            reasons.append("금칙어 포함")

        sources = self._collect_sources(collector_payload)
        sources_total = sum(sources.values())
        if sources_total < MIN_SOURCES_TOTAL:
            reasons.append(
                f"출처 수({sources_total})가 최소 기준({MIN_SOURCES_TOTAL}) 미달"
            )

        if sources_total:
            max_source_ratio = max(sources.values()) / sources_total
            if max_source_ratio > MAX_SINGLE_SOURCE_RATIO:
                reasons.append("동일 출처 비중 50% 초과")

        return {
            "pass": len(reasons) == 0,
            "reasons": reasons,
            "metrics": {
                "char_count": char_count,
                "item_count": item_count,
                "sources_total": sources_total,
                "sources_unique": len(sources),
            },
        }

    def _split_items(self, markdown: str) -> List[str]:
        blocks = []
        current = []
        for line in markdown.splitlines():
            if re.match(r"^\d+\)\s", line):
                if current:
                    blocks.append(" ".join(current).strip())
                current = [line]
            elif current:
                current.append(line)
        if current:
            blocks.append(" ".join(current).strip())
        return blocks

    def _count_sentences(self, text: str) -> int:
        sentences = re.findall(r"[^.!?]+[.!?]", text)
        return len(sentences)

    def _collect_sources(self, collector_payload: Dict[str, Any]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for item in collector_payload.get("items", []):
            for source in item.get("sources", []):
                name = source.get("name", "unknown")
                counts[name] = counts.get(name, 0) + 1
        return counts

    def _contains_number_without_date(self, text: str) -> bool:
        has_number = bool(re.search(r"\d", text))
        has_date = bool(re.search(r"\d{4}-\d{2}-\d{2}", text))
        has_marker = "기준시점" in text or "발표일" in text
        return has_number and not (has_date or has_marker)
