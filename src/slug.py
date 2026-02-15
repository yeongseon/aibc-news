from __future__ import annotations

import hashlib
import re
from typing import Dict, Any


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "news"


def _hash(value: str, size: int = 8) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:size]


def _symbol_slug(symbol: str) -> str:
    return symbol.lower().replace("^", "").replace("=", "-")


def make_post_id(item: Dict[str, Any]) -> str:
    item_type = item.get("type", "news")
    slug = item.get("slug")

    if not slug and item_type == "market":
        sources = item.get("sources", [])
        if sources:
            url = sources[0].get("url", "")
            symbol = url.split("/")[-1]
            slug = _symbol_slug(symbol)

    if not slug and item_type == "weather":
        slug = item.get("city", "kr")

    if not slug:
        title = item.get("title", "news")
        slug = f"{slugify(title)}-{_hash(title, 6)}"

    return f"{item_type}-{slug}"


def make_filename(run_date: str, item: Dict[str, Any]) -> str:
    post_id = make_post_id(item)
    return f"{run_date}-{post_id}.md"
