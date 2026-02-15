import json
import os
from typing import Any, Dict

import azure.functions as func
import requests


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


def main(req: func.HttpRequest) -> func.HttpResponse:
    payload = _get_payload(req)
    run_date = payload.get("run_date")
    category = payload.get("category")
    force = _bool_value(payload.get("force"))
    dry_run = _bool_value(payload.get("dry_run"))
    idempotency_key = payload.get("idempotency_key")

    if not category:
        return func.HttpResponse(
            json.dumps({"error": "Missing category"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    repo = os.environ.get("GITHUB_REPO") or os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")
    if not repo or not token:
        return func.HttpResponse(
            json.dumps({"error": "Missing GITHUB_REPO/GITHUB_TOKEN"}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )

    url = f"https://api.github.com/repos/{repo}/dispatches"
    body: Dict[str, Any] = {
        "event_type": "publish_article",
        "client_payload": {
            "category": category,
            "run_date": run_date,
            "force": force,
            "dry_run": dry_run,
            "max_chars": payload.get("max_chars"),
            "min_chars": payload.get("min_chars"),
        },
    }
    if idempotency_key:
        body["client_payload"]["idempotency_key"] = str(idempotency_key)

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json=body,
        timeout=15,
    )

    if response.status_code >= 300:
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "dispatch_failed",
                    "status": response.status_code,
                    "details": response.text,
                },
                ensure_ascii=False,
            ),
            status_code=500,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps(
            {
                "status": "queued",
                "event_type": "publish_article",
                "run_date": run_date,
                "category": category,
                "force": force,
                "dry_run": dry_run,
                "idempotency_key": idempotency_key,
            },
            ensure_ascii=False,
        ),
        status_code=202,
        mimetype="application/json",
    )
