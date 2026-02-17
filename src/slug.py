from __future__ import annotations

import hashlib
import re
from typing import Dict, Any


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "article"


def _hash(value: str, size: int = 8) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:size]


def _symbol_slug(symbol: str) -> str:
    return symbol.lower().replace("^", "").replace("=", "-")


def make_post_id(item: Dict[str, Any]) -> str:
    item_type = item.get("type", "politics")
    slug = item.get("slug")

    if not slug and item_type == "economy":
        sources = item.get("sources", [])
        if sources:
            url = sources[0].get("url", "")
            symbol = url.split("/")[-1]
            slug = _symbol_slug(symbol)

    if not slug and item_type == "weather":
        slug = item.get("city", "kr")

    if not slug:
        title = item.get("title", "article")
        slug = f"{slugify(title)}-{_hash(title, 6)}"

    return f"{item_type}-{slug}"


def _extract_time_token(value: str | None) -> str:
    if not value:
        return "0000"
    match = re.search(r"(\d{1,2}):(\d{2})", value)
    if not match:
        return "0000"
    hour = int(match.group(1))
    minute = int(match.group(2))
    return f"{hour:02d}{minute:02d}"


def make_filename(
    run_date: str, item: Dict[str, Any], published_at: str | None = None
) -> str:
    post_id = make_post_id(item)
    time_token = _extract_time_token(published_at)
    return f"{run_date}-{time_token}-{post_id}.md"
