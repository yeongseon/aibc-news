#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request

GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
SECRET_PATH = os.environ.get("SECRET_PATH", "")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "")


def dispatch(payload):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    body = {
        "event_type": "publish_article",
        "client_payload": payload,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if not self.path.endswith(SECRET_PATH):
            self.send_response(404)
            self.end_headers()
            return

        auth = self.headers.get("Authorization", "")
        if auth != f"Bearer {BEARER_TOKEN}":
            self.send_response(401)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            body = {}

        if not body.get("category"):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"missing category")
            return

        payload = {
            "category": body.get("category"),
            "run_date": body.get("run_date"),
            "force": bool(body.get("force")),
            "dry_run": bool(body.get("dry_run")),
            "idempotency_key": body.get("idempotency_key"),
            "max_chars": body.get("max_chars"),
            "min_chars": body.get("min_chars"),
        }

        status = dispatch(payload)
        self.send_response(202 if status in (200, 201, 202, 204) else 500)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "queued"}).encode("utf-8"))


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8081"))
    server = HTTPServer((host, port), Handler)
    server.serve_forever()
