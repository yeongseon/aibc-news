import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, List

import azure.functions as func

ROOT = Path(__file__).resolve().parents[2]


def _get_payload(req: func.HttpRequest) -> Dict[str, Any]:
    try:
        body = req.get_json()
    except ValueError:
        body = {}
    return body if isinstance(body, dict) else {}


def _bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).lower() == "true"


def _load_pipeline():
    import sys

    sys.path.insert(0, str(ROOT))
    from src.app import generate_posts
    from src.collector import CompositeCollector
    from src.publisher import Publisher
    from src.quality import QualityGate
    from src.slug import make_filename
    from src.utils import RunLogger, now_kst_date
    from src.writer import CopilotWriter

    return {
        "generate_posts": generate_posts,
        "collector": CompositeCollector(),
        "writer": CopilotWriter(),
        "gate": QualityGate(),
        "publisher": Publisher(),
        "make_filename": make_filename,
        "logger_factory": RunLogger,
        "now_kst_date": now_kst_date,
    }


def _category_for(item_type: str) -> str:
    mapping = {
        "market": "market",
        "weather": "weather",
        "lifestyle": "life",
        "headline": "news",
    }
    return mapping.get(item_type, "news")


def _filter_payload(payload: Dict[str, Any], category: str) -> Dict[str, Any]:
    filtered_items = [
        item
        for item in payload.get("items", [])
        if _category_for(item.get("type", "news")) == category
    ]
    return {"date": payload.get("date", ""), "items": filtered_items}


def _get_repo() -> str | None:
    return os.environ.get("GITHUB_REPO") or os.environ.get("GITHUB_REPOSITORY")


def _gh_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


def _github_get(url: str, headers: Dict[str, str]):
    import requests

    return requests.get(url, headers=headers, timeout=15)


def _github_put(url: str, headers: Dict[str, str], body: Dict[str, Any]):
    import requests

    return requests.put(url, headers=headers, json=body, timeout=15)


def _create_or_update_file(
    token: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    force: bool,
) -> Dict[str, Any]:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = _gh_headers(token)

    existing = _github_get(url, headers)
    sha = None
    if existing.status_code == 200:
        sha = existing.json().get("sha")
        if not force:
            return {"status": "skipped", "path": path}
    elif existing.status_code not in (404,):
        return {"status": "error", "path": path, "detail": existing.text}

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    body = {"message": message, "content": encoded}
    if sha:
        body["sha"] = sha

    response = _github_put(url, headers, body)
    if response.status_code >= 300:
        return {"status": "error", "path": path, "detail": response.text}

    return {"status": "published", "path": path}


def main(req: func.HttpRequest) -> func.HttpResponse:
    payload = _get_payload(req)
    run_date = payload.get("run_date")
    category = payload.get("category")
    force_publish = _bool_value(payload.get("force"))

    repo = _get_repo()
    token = os.environ.get("GITHUB_TOKEN")
    if not repo or not token:
        return func.HttpResponse(
            json.dumps({"error": "Missing GITHUB_REPO/GITHUB_TOKEN"}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )

    pipeline = _load_pipeline()
    if not run_date:
        run_date = pipeline["now_kst_date"]()

    logger = pipeline["logger_factory"](Path("/tmp") / "rest-publish.log")

    collector = pipeline["collector"]
    writer = pipeline["writer"]
    gate = pipeline["gate"]
    publisher = pipeline["publisher"]
    generate_posts = pipeline["generate_posts"]

    collected = collector.collect(run_date)
    if category:
        collected = _filter_payload(collected, category)

    drafts, _quality = generate_posts(
        collected,
        run_date,
        writer=writer,
        gate=gate,
        logger=logger,
    )

    results: List[Dict[str, Any]] = []
    for draft in drafts:
        post_result = publisher.publish(
            run_date=run_date,
            markdown_body=draft.markdown_body,
            summary=draft.summary,
            sources=draft.sources,
            category=draft.category,
            filename=draft.filename,
            dry_run=True,
            force=force_publish,
        )
        content = post_result.get("content", "")
        path = f"_posts/{draft.filename}"
        message = f"REST publish: {draft.filename}"
        results.append(
            _create_or_update_file(
                token=token,
                repo=repo,
                path=path,
                content=content,
                message=message,
                force=force_publish,
            )
        )

    status_code = 202 if any(r["status"] == "published" for r in results) else 200

    return func.HttpResponse(
        json.dumps(
            {
                "status": "ok",
                "run_date": run_date,
                "category": category,
                "force": force_publish,
                "results": results,
            },
            ensure_ascii=False,
        ),
        status_code=status_code,
        mimetype="application/json",
    )
