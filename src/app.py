from __future__ import annotations

from typing import Any, Dict, List

from .domain.models import CollectorPayload, PostDraft
from .config import CATEGORY_LABELS
from .slug import make_filename


class QualityGateError(RuntimeError):
    def __init__(self, quality_results: List[Dict[str, Any]], reasons: List[str]):
        super().__init__("Quality gate failed")
        self.quality_results = quality_results
        self.reasons = reasons


def generate_posts(
    payload: Dict[str, Any],
    run_date: str,
    *,
    writer,
    gate,
    logger,
) -> tuple[List[PostDraft], List[Dict[str, Any]]]:
    typed_payload = CollectorPayload.from_dict(payload)
    drafts: List[PostDraft] = []
    quality_results: List[Dict[str, Any]] = []

    for item in typed_payload.items:
        item_payload = item.to_dict()
        logger.log("Writer start")
        markdown_body, summary = writer.write_item(item_payload, run_date)
        logger.log("Quality gate start")
        quality_result = gate.validate(markdown_body, {"items": [item_payload]})

        quality_results.append(
            {
                "type": item_payload.get("type", "politics"),
                "title": item_payload.get("title", ""),
                "quality": quality_result,
            }
        )

        passed = (
            quality_result.get("pass")
            if isinstance(quality_result, dict)
            else quality_result.passed
        )
        if not passed:
            reasons = (
                quality_result.get("reasons")
                if isinstance(quality_result, dict)
                else quality_result.reasons
            )
            logger.log(f"Quality gate failed: {reasons}")
            raise QualityGateError(quality_results, reasons)

        category = _category_for(item_payload.get("type", "politics"))
        filename = make_filename(run_date, item_payload)
        raw_title = item_payload.get("title", "")
        title = _normalize_title(raw_title, category)
        drafts.append(
            PostDraft(
                category=category,
                filename=filename,
                markdown_body=markdown_body,
                summary=summary,
                sources=item_payload.get("sources", []),
                title=title,
                image=item_payload.get("image"),
            )
        )

    return drafts, quality_results


def publish_posts(drafts: List[PostDraft], *, publisher, dry_run: bool, force: bool) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for draft in drafts:
        result = publisher.publish(
            run_date="",
            markdown_body=draft.markdown_body,
            summary=draft.summary,
            sources=draft.sources,
            category=draft.category,
            filename=draft.filename,
            title=draft.title,
            image=draft.image,
            dry_run=dry_run,
            force=force,
        )
        results.append(result)
    return results


def _category_for(item_type: str) -> str:
    mapping = {
        "politics": "politics",
        "economy": "economy",
        "society": "society",
        "world": "world",
        "tech": "tech",
        "culture": "culture",
        "sports": "sports",
        "entertainment": "entertainment",
        "life": "life",
        "weather": "weather",
    }
    return mapping.get(item_type, "politics")


def _normalize_title(raw_title: str, category: str) -> str:
    prefix = CATEGORY_LABELS.get(category, category)
    title = raw_title.strip()
    if prefix and not title.startswith(prefix):
        title = f"[{prefix}] {title}"
    # normalize length 18-26 chars
    title = title[:26]
    if len(title) < 18:
        title = (title + " " * 18)[:18].strip()
    return title
