import re
from typing import List

from ..config import MAX_ITEMS, MAX_SENTENCES, MIN_ITEMS, MIN_SENTENCES


def split_items(markdown: str) -> List[str]:
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


def count_sentences(text: str) -> int:
    sentences = re.findall(r"[^.!?]+[.!?]", text)
    return len(sentences)


def validate_writer_output(markdown: str) -> None:
    items = split_items(markdown)
    if not (MIN_ITEMS <= len(items) <= MAX_ITEMS):
        raise ValueError("Writer item count out of range")

    for item in items:
        sentence_count = count_sentences(item)
        if not (MIN_SENTENCES <= sentence_count <= MAX_SENTENCES):
            raise ValueError("Writer sentence count out of range")
