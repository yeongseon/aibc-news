from typing import Dict, Any


REQUIRED_ITEM_KEYS = {"type", "title", "facts", "sources"}
REQUIRED_SOURCE_KEYS = {"name", "url", "published_at"}
ALLOWED_TYPES = {"headline", "market", "weather", "lifestyle"}


def validate_payload(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("Collector payload must be a dict")

    if "date" not in payload or "items" not in payload:
        raise ValueError("Collector payload requires date and items")

    items = payload["items"]
    if not isinstance(items, list) or not items:
        raise ValueError("Collector items must be a non-empty list")

    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Each item must be a dict")
        if not REQUIRED_ITEM_KEYS.issubset(item.keys()):
            raise ValueError("Item missing required keys")
        if item["type"] not in ALLOWED_TYPES:
            raise ValueError("Item type must be headline/market/weather/lifestyle")
        if not isinstance(item["facts"], list) or not item["facts"]:
            raise ValueError("Item facts must be a non-empty list")
        if not isinstance(item["sources"], list) or not item["sources"]:
            raise ValueError("Item sources must be a non-empty list")

        for source in item["sources"]:
            if not isinstance(source, dict):
                raise ValueError("Source must be a dict")
            if not REQUIRED_SOURCE_KEYS.issubset(source.keys()):
                raise ValueError("Source missing required keys")
            if not source["name"] or not source["url"] or not source["published_at"]:
                raise ValueError("Source fields must be non-empty")
