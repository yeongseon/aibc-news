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


def _bool_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "false"
    return str(value).lower()


def main(req: func.HttpRequest) -> func.HttpResponse:
    payload = _get_payload(req)
    run_date = payload.get("run_date")
    dry_run = _bool_value(payload.get("dry_run"))
    force_publish = _bool_value(payload.get("force_publish"))
    idempotency_key = payload.get("idempotency_key")

    repo = os.environ.get("GITHUB_REPO") or os.environ.get("GITHUB_REPOSITORY")
    workflow_id = os.environ.get("WORKFLOW_ID", "daily-brief.yml")
    ref = os.environ.get("GITHUB_REF", "main")
    token = os.environ.get("GITHUB_TOKEN")

    if not repo or not token:
        return func.HttpResponse(
            json.dumps({"error": "Missing GITHUB_REPO/GITHUB_TOKEN"}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )

    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches"
    inputs: Dict[str, str] = {}
    if run_date:
        inputs["run_date"] = run_date
    if dry_run:
        inputs["dry_run"] = dry_run
    if force_publish:
        inputs["force_publish"] = force_publish
    if idempotency_key:
        inputs["idempotency_key"] = str(idempotency_key)

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={"ref": ref, "inputs": inputs},
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
                "workflow": workflow_id,
                "run_date": run_date,
                "dry_run": dry_run,
                "force_publish": force_publish,
                "idempotency_key": idempotency_key,
            },
            ensure_ascii=False,
        ),
        status_code=202,
        mimetype="application/json",
    )
