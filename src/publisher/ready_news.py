from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ..config import CATEGORY_LABELS
from ..slug import make_filename
from .publisher import Publisher


def load_ready_items(
    *, ready_dir: Path, run_date: str, category: str | None = None
) -> List[Dict[str, Any]]:
    date_dir = ready_dir / run_date
    if not date_dir.exists():
        raise FileNotFoundError(f"Ready news directory not found: {date_dir}")

    files = sorted(date_dir.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No ready news files found in: {date_dir}")

    items: List[Dict[str, Any]] = []
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = payload.get("items") if isinstance(payload, dict) else None
        if isinstance(entries, list):
            raw_items = entries
        else:
            raw_items = [payload]

        for raw in raw_items:
            if not isinstance(raw, dict):
                raise ValueError(f"Invalid item format in {path}")

            normalized = dict(raw)
            normalized["date"] = str(normalized.get("date") or run_date)
            normalized["category"] = str(
                normalized.get("category") or (category or "")
            ).strip()
            _validate_item(normalized, path)

            if category and normalized["category"] != category:
                continue
            items.append(normalized)

    if not items:
        raise RuntimeError("No ready news items matched the requested category/date")

    return items


def publish_ready_items(
    items: List[Dict[str, Any]],
    *,
    dry_run: bool,
    force: bool,
    posts_dir: Path | None = None,
) -> List[Dict[str, Any]]:
    publisher = Publisher(posts_dir=posts_dir)
    results: List[Dict[str, Any]] = []

    for item in items:
        item_payload = {
            "type": item["category"],
            "title": item["title"],
            "slug": item.get("slug"),
            "sources": item["sources"],
        }
        filename = item.get("filename") or make_filename(item["date"], item_payload)

        image_url = _resolve_image_url(item)

        result = publisher.publish(
            run_date=item["date"],
            markdown_body=item["body"],
            summary=item["summary"],
            sources=item["sources"],
            category=item["category"],
            filename=filename,
            title=item["title"],
            image=image_url,
            dry_run=dry_run,
            force=force,
        )
        results.append(result)

    return results


def _validate_item(item: Dict[str, Any], path: Path) -> None:
    for key in ("date", "category", "title", "summary", "body", "sources"):
        if key not in item or item[key] in (None, ""):
            raise ValueError(f"Missing required field '{key}' in {path}")

    category = item["category"]
    if category not in CATEGORY_LABELS:
        raise ValueError(f"Unsupported category '{category}' in {path}")

    if not isinstance(item["sources"], list) or not item["sources"]:
        raise ValueError(f"Field 'sources' must be a non-empty list in {path}")

    for source in item["sources"]:
        if (
            not isinstance(source, dict)
            or not source.get("name")
            or not source.get("url")
        ):
            raise ValueError(f"Each source must include 'name' and 'url' in {path}")

    media = item.get("media")
    if media is not None:
        if not isinstance(media, dict):
            raise ValueError(f"Field 'media' must be an object in {path}")
        hero_image = media.get("hero_image")
        if not isinstance(hero_image, dict):
            raise ValueError(f"Field 'media.hero_image' must be an object in {path}")
        if not hero_image.get("url"):
            raise ValueError(f"Field 'media.hero_image.url' is required in {path}")
        if not hero_image.get("alt"):
            raise ValueError(f"Field 'media.hero_image.alt' is required in {path}")

    generation = item.get("generation")
    if generation is not None:
        if not isinstance(generation, dict):
            raise ValueError(f"Field 'generation' must be an object in {path}")
        reporter_id = generation.get("reporter_id")
        if reporter_id is not None and not str(reporter_id).strip():
            raise ValueError(
                f"Field 'generation.reporter_id' must be non-empty in {path}"
            )


def _resolve_image_url(item: Dict[str, Any]) -> str | None:
    media = item.get("media")
    if isinstance(media, dict):
        hero_image = media.get("hero_image")
        if isinstance(hero_image, dict):
            url = hero_image.get("url")
            if isinstance(url, str) and url.strip():
                return url.strip()

    image = item.get("image")
    if isinstance(image, str) and image.strip():
        return image.strip()

    return None
